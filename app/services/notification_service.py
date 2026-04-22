"""Expo push notification service.

Sends push notifications via the Expo Push API using only stdlib (urllib).
Notifications are best-effort: failures are silently ignored so they never
break the main request flow.
"""

import json
import urllib.request
import urllib.error

EXPO_PUSH_URL = 'https://exp.host/--/exponent-push-server/api/v2/push/send'


def send_push_notifications(user_ids, title, body, data=None):
    """Send Expo push notifications to all registered devices for the given user IDs.

    Parameters:
        user_ids (list[int]): Target user IDs.
        title    (str):       Notification title.
        body     (str):       Notification body text.
        data     (dict):      Extra payload forwarded to the app (e.g. request_id).
    """
    from app.model.device_token import DeviceToken

    if not user_ids:
        return

    tokens = DeviceToken.query.filter(DeviceToken.user_id.in_(user_ids)).all()
    if not tokens:
        return

    messages = [
        {
            'to': t.token,
            'title': title,
            'body': body,
            'data': data or {},
            'sound': 'default',
        }
        for t in tokens
    ]

    payload = json.dumps(messages).encode('utf-8')
    req = urllib.request.Request(
        EXPO_PUSH_URL,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
    except (urllib.error.URLError, OSError):
        pass
