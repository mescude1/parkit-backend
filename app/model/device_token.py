from datetime import datetime

from sqlalchemy import ForeignKey

from app.database import db


class DeviceToken(db.Model):
    """
    Stores Expo push notification tokens for users.

    One user may have multiple tokens (multiple devices). Tokens are unique
    across the table — if a token is registered by a new user it transfers.
    """

    __tablename__ = 'device_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
