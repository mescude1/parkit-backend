# Valet Service API — Mobile Integration Guide

This document covers everything the Expo Go app needs to implement the valet request and acceptance flow end-to-end.

---

## Base URL

```
http://<server-host>:<port>
```

All requests that require authentication must include the JWT token obtained at login:

```
Authorization: Bearer <access_token>
```

---

## Overview of the Flow

```
CLIENT APP                          SERVER                        VALET APP
    |                                  |                               |
    |-- POST /device-token/register -->|                               |
    |                                  |<-- POST /device-token/register|
    |                                  |                               |
    |-- POST /valet/request ---------->|                               |
    |   { latitude, longitude }        |-- push notification --------->|
    |<-- { request_id, status } -------|   { request_id }              |
    |                                  |                               |
    |   [polling GET /valet/request/id]|   [valet taps notification]   |
    |                                  |<-- POST /valet/request/id/accept
    |<-- push: "Valet en camino" ------|   { latitude, longitude }     |
    |                                  |-- { service_id,               |
    |                                  |    client_location } -------->|
    |                                  |                               |
    |   [both sides exchange location updates every ~3 s]              |
    |-- POST /valet/location/update -->|<-- POST /valet/location/update|
    |<-- GET /valet/location/valet_id -|-- GET /valet/location/client_id
```

---

## 1. Push Notifications Setup

### 1.1 Get the Expo push token (client side)

```js
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

async function registerForPushNotifications() {
  if (!Device.isDevice) return null; // won't work in simulator

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  const token = (await Notifications.getExpoPushTokenAsync()).data;
  // token looks like: "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
  return token;
}
```

### 1.2 Register the token with the backend

Call this once **after login**, every session.

```
POST /device-token/register
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
}
```

**Response 201 / 200**
```json
{ "message": "Token registered" }
```

### 1.3 Unregister on logout

```
DELETE /device-token/unregister
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
}
```

**Response 200**
```json
{ "message": "Token unregistered" }
```

### 1.4 Listen for incoming notifications

```js
import * as Notifications from 'expo-notifications';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

// In your root component:
useEffect(() => {
  const sub = Notifications.addNotificationReceivedListener(notification => {
    const { type, request_id, service_id, valet_id } = notification.request.content.data;

    if (type === 'valet_request') {
      // Valet app: a new request is nearby
      // navigate to accept screen with request_id
    }

    if (type === 'valet_accepted') {
      // Client app: a valet accepted
      // navigate to tracking screen with service_id, valet_id
    }
  });
  return () => sub.remove();
}, []);
```

**Notification payloads**

| `type` | Recipient | Extra fields |
|--------|-----------|--------------|
| `valet_request` | Valet | `request_id` |
| `valet_accepted` | Client | `service_id`, `valet_id` |

---

## 2. Client Flow — Request a Valet

### 2.1 Get the device's current location

```js
import * as Location from 'expo-location';

const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== 'granted') { /* handle */ }

const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
// loc.coords.latitude, loc.coords.longitude
```

### 2.2 Create a valet request

```
POST /valet/request
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "latitude": 4.710989,
  "longitude": -74.072092
}
```

**Response 201**
```json
{
  "request_id": 42,
  "status": "pending",
  "nearby_valets_notified": 3
}
```

**Error responses**

| Status | Meaning |
|--------|---------|
| 400 | Missing latitude or longitude |
| 403 | Caller is not a `cliente` |

Store `request_id` — you will need it to poll status and to cancel.

### 2.3 Poll request status

Call this every **3–5 seconds** until `status` is `"accepted"` or `"cancelled"`.

```
GET /valet/request/<request_id>
Authorization: Bearer <access_token>
```

**Response 200 — pending**
```json
{
  "id": 42,
  "client_id": 7,
  "latitude": 4.710989,
  "longitude": -74.072092,
  "status": "pending",
  "accepted_by": null,
  "service_id": null,
  "created_at": "2026-03-28T14:30:00"
}
```

**Response 200 — accepted** (includes valet's live location)
```json
{
  "id": 42,
  "status": "accepted",
  "accepted_by": 15,
  "service_id": 8,
  "created_at": "2026-03-28T14:30:00",
  "valet_location": {
    "id": 301,
    "user_id": 15,
    "latitude": 4.711200,
    "longitude": -74.071800,
    "timestamp": "2026-03-28T14:31:05",
    "type": "live"
  }
}
```

When `status === "accepted"`, switch the UI to the **tracking screen** and start the location update loop (section 4).

### 2.4 Cancel a request

Only works while `status === "pending"`.

```
POST /valet/request/<request_id>/cancel
Authorization: Bearer <access_token>
```

**Response 200**
```json
{ "message": "Request cancelled", "request_id": 42 }
```

---

## 3. Valet Flow — Accept a Request

The valet receives a push notification with `{ type: "valet_request", request_id: 42 }`.

### 3.1 Accept the request

```
POST /valet/request/<request_id>/accept
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "latitude": 4.711200,
  "longitude": -74.071800
}
```

The body is optional but recommended — it lets the server record the valet's starting position and return it to the client immediately.

**Response 200**
```json
{
  "service_id": 8,
  "request_id": 42,
  "message": "Service started",
  "client_location": {
    "id": 298,
    "user_id": 7,
    "latitude": 4.710989,
    "longitude": -74.072092,
    "timestamp": "2026-03-28T14:30:01",
    "type": "live"
  }
}
```

**Error responses**

| Status | Meaning |
|--------|---------|
| 403 | Caller is not a `valet` |
| 404 | Request not found |
| 409 | Request already accepted / cancelled |

After accepting, use `client_location` to initialize the map and start the location update loop (section 4).

---

## 4. Real-time Location Tracking

Both parties push their own location and pull the other party's location every **3–5 seconds** while the service is active.

### 4.1 Push your own location

```
POST /valet/location/update
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "latitude": 4.711100,
  "longitude": -74.071900
}
```

**Response 200**
```json
{ "message": "Location updated" }
```

### 4.2 Pull the other party's location

```
GET /valet/location/<user_id>
Authorization: Bearer <access_token>
```

**Response 200**
```json
{
  "id": 305,
  "user_id": 15,
  "latitude": 4.711150,
  "longitude": -74.071850,
  "timestamp": "2026-03-28T14:32:10",
  "type": "live"
}
```

**Response 404** — no location recorded yet for this user.

### 4.3 Suggested polling loop (React Native)

```js
useEffect(() => {
  // Push our location
  const pushInterval = setInterval(async () => {
    const loc = await Location.getCurrentPositionAsync({});
    await fetch(`${BASE_URL}/valet/location/update`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ latitude: loc.coords.latitude, longitude: loc.coords.longitude }),
    });
  }, 3000);

  // Pull other party's location
  const pullInterval = setInterval(async () => {
    const res = await fetch(`${BASE_URL}/valet/location/${otherUserId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setOtherPartyCoords({ latitude: data.latitude, longitude: data.longitude });
    }
  }, 3000);

  return () => {
    clearInterval(pushInterval);
    clearInterval(pullInterval);
  };
}, []);
```

---

## 5. End Service

```
POST /valet/end-service
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "service_id": 8
}
```

**Response 200**
```json
{ "status": "success", "message": "Service ended" }
```

---

## 6. User Type Reference

The `type` field on the user object controls which endpoints are accessible:

| `type` | Can call |
|--------|----------|
| `cliente` | `POST /valet/request`, `POST /valet/request/<id>/cancel` |
| `valet` | `POST /valet/request/<id>/accept`, `POST /valet/end-service` |
| both | `POST /valet/location/update`, `GET /valet/location/<id>`, `GET /valet/request/<id>` |

---

## 7. Full Screen Map — Recommended Libraries

```bash
npx expo install react-native-maps expo-location expo-notifications expo-device
```

| Library | Use |
|---------|-----|
| `react-native-maps` | Render map with markers for both parties |
| `expo-location` | Get device GPS coordinates |
| `expo-notifications` | Receive and handle push notifications |
| `expo-device` | Check if running on a real device (required for push) |

---

## 8. Typical State Machine (Client UI)

```
IDLE
  └─ tap "Request Valet" → REQUESTING
       └─ POST /valet/request
            ├─ error (no valets nearby) → IDLE
            └─ success → WAITING_FOR_VALET
                  ├─ poll GET /valet/request/<id> every 4 s
                  ├─ tap "Cancel" → POST /valet/request/<id>/cancel → IDLE
                  └─ status === "accepted"  OR  push "valet_accepted"
                        └─ TRACKING (show map, start location loop)
                              └─ service ends → IDLE
```

## 9. Typical State Machine (Valet UI)

```
IDLE (waiting for notifications)
  └─ push notification { type: "valet_request", request_id }
        └─ show accept screen
              ├─ tap "Decline" → IDLE
              └─ tap "Accept" → POST /valet/request/<id>/accept
                    └─ NAVIGATING (show client location on map, start location loop)
                          └─ POST /valet/end-service → IDLE
```
