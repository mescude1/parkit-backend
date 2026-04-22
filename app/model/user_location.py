from sqlalchemy import ForeignKey

from app.database import db


class UserLocation(db.Model):
    """
    Represents a user's location data within the application.

    This class defines a model for storing user location data, including the URL
    of the location, the associated image name, its owner, type, creation
    timestamp, and whether it has been marked as deleted. It is intended to be
    used in conjunction with an SQLAlchemy database.

    Attributes:
        id: The unique identifier for the user location.
        url: The URL associated with the user's location.
        image_name: The name of the image file associated with the location.
        owner: The identifier of the user who owns this location.
        type: The type or category of the location.
        created_at: The timestamp when the location entry was created.
        is_deleted: A flag indicating if the location has been logically deleted.

    Methods:
        to_dict: Converts the user location instance into a dictionary
        representation.
    """

    __tablename__ = 'user_locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp,
            'type': self.type
        }
