from sqlalchemy import ForeignKey

from app.database import db


class MediaMetadata(db.Model):
    """
    Represents metadata information for media in the database.

    The MediaMetadata class maps to the 'media_metadata' table in the database
    and stores information about media files, including their URL, associated
    name, owner, type, creation timestamp, and deletion status. It provides
    methods to access and manipulate this information, making it useful for
    applications managing media data.

    Attributes:
        id (int): Unique identifier for the media entry.
        url (str): URL of the media file.
        image_name (str): Name of the media file.
        owner (int): Identifier of the user who owns the media file.
        type (str): Type of the media (e.g., image, video).
        created_at (datetime): Timestamp when the media entry was created.
        is_deleted (bool): Indicates whether the media entry is marked as deleted.
    """

    __tablename__ = 'media_metadata'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    image_name = db.Column(db.String, nullable=False)
    owner = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'image_name': self.image_name,
            'owner': self.owner,
            'type': self.type,
            'created_at': self.created_at,
        }
