"""It contains MediaMetadataRepository class."""

from app.model.media_metadata import MediaMetadata
from app.model.repository import Repository


class MediaMetadataRepository(Repository):
    """It Contains specific method related to de User
    model to do operation in the database.
    """

    def __init__(self):
        Repository.__init__(self, MediaMetadata)

    def save(self, media_metadata: MediaMetadata) -> None:
        """Saves a media_metadata in the database.

        Parameters:
           model (MediaMetadata): A media_metadata model object.
        """

        self.session.add(media_metadata)
        self.session.commit()

    def update(self, media_metadata: MediaMetadata) -> None:
        """Update a existent user in the database.

        Parameters:
           model (object): A user model object.
        """

        self.session.commit()

    def delete(self, media_metadata: MediaMetadata) -> None:
        """Delete a media_metadata from the database.

            Parameters:
               media_metadata (Vehicle): The media_metadata model object to be deleted.
            """
        self.session.delete(media_metadata)
        self.session.commit()
