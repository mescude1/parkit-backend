# ParkIT API Reference

**Base URL**: `http://<server>:<port>`
**Auth**: JWT Bearer token — include `Authorization: Bearer <access_token>` on protected routes
**Content-Type**: `application/json` on all POST/PUT/PATCH requests

---

## Notes on Registered Endpoints

Only the following blueprints are **currently active**. Endpoints marked _(not registered)_ exist in code but are not accessible.

| Blueprint | Prefix | Status |
|-----------|--------|--------|
| index | `/` | Active |
| autho | `/autho` | Active |
| register | `/register` | Active |
| verification | `/verification` | Active |
| valet | `/valet` | Active |
| profile | `/profile` | Not registered |
| vehicles | `/vehicles` | Not registered |
| account | `/account` | Not registered |
| display | `/display` | Not registered |

---

## Health Check

### `GET /`
Returns server status.

**Auth**: None

**Response `200`**
```
"The server is running!"
```

---

## Authentication

### `POST /autho/login`
Authenticate and receive a JWT token.

**Auth**: None

**Request body**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response `200`**
```json
{
  "data": {
    "user": { /* User object — see User Schema */ },
    "access_token": "string"
  }
}
```

**Response `401`**
```json
{
  "status": "error",
  "data": "401 Unauthorized"
}
```

---

### `POST /autho/logout`
Revoke the current JWT token (blacklists it server-side).

**Auth**: Required

**Request body**: None

**Response `200`**
```json
{
  "status": "success",
  "message": "Logged out"
}
```

---

## Registration

### `POST /register/valet`
Register a new valet (driver) account.

**Auth**: None

**Request body**
```json
{
  "name":               "string",
  "last_name":          "string",
  "username":           "string (unique)",
  "password":           "string (min 6 chars)",
  "email":              "string (valid email, unique)",
  "cellphone":          "string",
  "vehicle_type":       "string",
  "profile_img":        "string (URL)",
  "id_img":             "string (URL — ID/cedula photo)",
  "driver_license_img": "string (URL)"
}
```

**Response `201`**
```json
{
  "status": "success",
  "message": "Valet registrado y verificado exitosamente.",
  "data": { /* User object */ }
}
```

**Response `409`** — username or email already in use
```json
{
  "status": "error",
  "message": "El nombre de usuario ya esta en uso"
}
```

**Response `422`** — validation errors
```json
{
  "status": "error",
  "message": "Datos invalidos",
  "errors": [{ "fieldname": "error message" }]
}
```

---

### `GET /register/valet/identity/<valet_code>`
Get the public identity of a verified valet by their code (`VAL-XXXXX` format).

**Auth**: None

**Response `200`**
```json
{
  "status": "success",
  "data": {
    "valet_code":  "string (VAL-XXXXX)",
    "name":        "string",
    "last_name":   "string",
    "profile_img": "string (URL)",
    "id_img":      "string (URL)",
    "vehicle_type":"string",
    "is_verified": true
  }
}
```

**Response `404`** — valet not found
**Response `403`** — valet is inactive or not yet verified

---

### `POST /register/cliente`
Register a new cliente (vehicle owner / student) account.
A 6-digit verification code is automatically emailed to `institutional_email`.

**Auth**: None

**Request body**
```json
{
  "name":                "string",
  "last_name":           "string",
  "username":            "string (unique)",
  "password":            "string (min 6 chars)",
  "email":               "string (personal email, unique)",
  "institutional_email": "string (@gmail.com address, unique)",
  "cellphone":           "string",
  "profile_img":         "string (URL)",
  "id_img":              "string (URL — ID/cedula photo)"
}
```

**Response `201`**
```json
{
  "status": "success",
  "message": "Cliente registrado. Se envio un codigo de verificacion a tu correo institucional.",
  "data": { /* User object — institutional_email_verified: false */ }
}
```

**Response `409`** — username, personal email, or institutional email already in use
**Response `422`** — validation errors (same shape as valet registration)

---

## Email Verification (Clientes only)

### `POST /verification/verify-email`
Verify a cliente's institutional email with the 6-digit code sent on registration.
Codes expire after **15 minutes**.

**Auth**: None

**Request body**
```json
{
  "user_id": "integer",
  "code":    "string (6 digits)"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Correo institucional verificado exitosamente",
  "data": { /* User object — institutional_email_verified: true */ }
}
```

**Response `400`** — missing fields, no pending code, expired code, or wrong code
**Response `404`** — user not found

---

### `POST /verification/resend-code`
Request a new verification code.

**Auth**: None

**Request body**
```json
{
  "user_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Nuevo codigo enviado a <institutional_email>"
}
```

**Response `400`** — missing user_id or email already verified
**Response `404`** — user not found

---

## Valet Service

> **Note**: Auth on these endpoints is partially implemented (JWT parsing is present but the `@jwt_required` decorator is commented out). Treat these as effectively unauthenticated for now.

---

### `POST /valet/request-service`
Find nearby valet drivers within 500 m of the given coordinates.

**Auth**: None (JWT optional)

**Request body**
```json
{
  "latitude":  "float",
  "longitude": "float"
}
```

**Response `200`** — drivers found
```json
{
  "message": "Drivers notified",
  "drivers": [1, 2, 3]
}
```

**Response `200`** — no drivers
```json
{
  "message": "No nearby drivers found"
}
```

**Response `400`** — missing coordinates
**Response `404`** — user not found

---

### `POST /valet/start-service`
Start a valet service between the current user and a target driver.
Returns location data, ETA (calculated at 5 km/h walking speed), and a fixed price.

**Auth**: None (JWT optional)

**Request body**
```json
{
  "target_user_id": "integer"
}
```

**Response `201`**
```json
{
  "message": "Service created successfully",
  "service_id": "integer",
  "user_location": {
    "latitude":  "float",
    "longitude": "float"
  },
  "target_location": {
    "latitude":  "float",
    "longitude": "float"
  },
  "eta_minutes":  "float",
  "fixed_price":  50.00
}
```

**Response `400`** — user or target location unavailable

---

### `POST /valet/end-service`
Mark an active service as completed.

**Auth**: None (JWT optional)

**Request body**
```json
{
  "service_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Service ended",
  "details": { }
}
```

---

### `POST /valet/cancel-service`
Cancel an active service.

**Auth**: None (JWT optional)

**Request body**
```json
{
  "service_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Service canceled",
  "details": { }
}
```

---

### `POST /valet/pre-service-photo`
Upload a photo before service begins.

**Auth**: Required

**Request body**
```json
{
  "photo_url":  "string (URL)",
  "service_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Pre-service photo uploaded",
  "details": { }
}
```

---

### `POST /valet/post-service-photo`
Upload a photo after service is complete.

**Auth**: Required

**Request body**
```json
{
  "photo_url":  "string (URL)",
  "service_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Post-service photo uploaded",
  "details": { }
}
```

---

### `POST /valet/key-photo`
Upload a photo of vehicle keys.

**Auth**: Required

**Request body**
```json
{
  "photo_url":  "string (URL)",
  "service_id": "integer"
}
```

**Response `200`**
```json
{
  "status": "success",
  "message": "Key photo uploaded",
  "details": { }
}
```

---

## Unregistered Endpoints (not yet accessible)

The following blueprints exist in code but are not registered in the app factory. They cannot be called.

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/profile/register` | Legacy registration |
| GET | `/profile/user-profile` | Get own profile |
| POST | `/profile/edit-profile` | Edit own profile |
| POST | `/profile/generate-enrollment-contracts` | Generate enrollment contract |
| POST | `/vehicles/new-vehicle` | Register a vehicle |
| POST | `/vehicles/edit-vehicle/<id>` | Edit a vehicle |
| GET | `/vehicles/vehicle/<id>` | Get one vehicle |
| GET | `/vehicles/vehicles` | Get all vehicles for user |
| GET | `/account` | Get account details |
| PUT | `/account` | Full account update (requires password) |
| PATCH | `/account` | Partial account update |
| DELETE | `/account` | Delete account |
| GET | `/display/dashboard` | Dashboard with recent services |
| GET | `/display/services` | List services |
| GET | `/display/vehicles` | List vehicles |

---

## Shared Schemas

### User Object
Returned by login, registration, and profile endpoints.

```json
{
  "id":                            "integer",
  "username":                      "string",
  "name":                          "string",
  "last_name":                     "string",
  "email":                         "string",
  "cellphone":                     "string",
  "type":                          "string (\"valet\" | \"cliente\")",
  "profile_img":                   "string (URL)",
  "id_img":                        "string (URL)",
  "driver_license_img":            "string (URL) | null",
  "contract":                      "string (URL) | null",
  "vehicle_type":                  "string | null",
  "created_at":                    "datetime (ISO 8601)",
  "is_deleted":                    "boolean",
  "is_verified":                   "boolean",
  "valet_code":                    "string (VAL-XXXXX) | null  — valets only",
  "institutional_email":           "string | null             — clientes only",
  "institutional_email_verified":  "boolean | null            — clientes only"
}
```

### Global Error Responses

| Status | Body |
|--------|------|
| `400` | `{ "status": "fail", "message": "bad request" }` |
| `404` | `{ "status": "error", "message": "not Found" }` |
| `401` (JWT missing/invalid) | Flask-JWT-Extended default error |

---

## Environment Notes

| Concern | Details |
|---------|---------|
| Password hashing | SHA-256 (not bcrypt) |
| Token blacklist | In-memory — tokens are not revoked across server restarts |
| Verification code store | In-memory — codes are lost on server restart |
| Email | Gmail SMTP on port 587 (requires `MAIL_USERNAME` / `MAIL_PASSWORD` env vars) |
| CORS | Enabled globally — all origins allowed |
| JWT secret | `dev` in development — **must be changed for production** |