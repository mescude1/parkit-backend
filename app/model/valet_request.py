from datetime import datetime

from sqlalchemy import ForeignKey

from app.database import db


class ValetRequest(db.Model):
    """
    Tracks a client's pending valet service request.

    Lifecycle: pending → accepted | cancelled | expired

    Attributes:
        client_id:   The client who created the request.
        latitude:    Client's latitude at time of request.
        longitude:   Client's longitude at time of request.
        status:      'pending' | 'accepted' | 'cancelled' | 'expired'
        accepted_by: The valet who accepted (nullable until accepted).
        service_id:  The Service record created on acceptance (nullable).
    """

    __tablename__ = 'valet_requests'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')
    accepted_by = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    service_id = db.Column(db.Integer, ForeignKey('services.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'accepted_by': self.accepted_by,
            'service_id': self.service_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
