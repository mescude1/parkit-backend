"""It contains ServiceRepository class."""

from app.model.service import Service
from app.model.repository import Repository


class ServiceRepository(Repository):
    """It Contains specific method related to de User
    model to do operation in the database.
    """

    def __init__(self):
        Repository.__init__(self, Service)

    def save(self, service: Service) -> None:
        """Saves a service in the database.

        Parameters:
           model (Service): A service model object.
        """

        self.session.add(service)
        self.session.commit()

    def update(self, service: Service) -> None:
        """Update a existent user in the database.

        Parameters:
           model (object): A user model object.
        """

        self.session.commit()

    def delete(self, service: Service) -> None:
        """Delete a service from the database.

            Parameters:
               service (Vehicle): The service model object to be deleted.
            """
        self.session.delete(service)
        self.session.commit()
