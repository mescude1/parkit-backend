"""It contains VehicleRepository class."""

from app.model.vehicle import Vehicle
from app.model.repository import Repository


class VehicleRepository(Repository):
    """
    Manages operations related to vehicles in the database, providing methods for
    retrieving, saving, updating, and deleting Vehicle model objects.

    This class acts as a specialized repository for handling database interactions
    specifically for the Vehicle model. It extends the base repository class and
    includes additional methods tailored for querying vehicles by specific fields
    such as license plate and owner ID.
    """

    def __init__(self):
        Repository.__init__(self, Vehicle)

    def get_by_license_plate(self, license_plate: str) -> Vehicle:
        """Retrieve a vehicle from the database by its license plate.

            Parameters:
               license_plate (str): The license plate of the vehicle.

            Returns:
                Vehicle: Vehicle model object if found, otherwise None.
            """
        return self.session.query(Vehicle).filter_by(license_plate=license_plate).first()

    def get_by_owner_id(self, owner_id: int) -> list[Vehicle]:
        """Retrieve vehicles from the database by their owner ID.

            Parameters:
               owner_id (int): The ID of the owner.

            Returns:
                list[Vehicle]: A list of Vehicle model objects associated with the owner.
            """
        return self.session.query(Vehicle).filter_by(owner=owner_id, is_deleted=False).all()

    def save(self, vehicle: Vehicle) -> None:
        """Saves a vehicle in the database.

        Parameters:
           model (Vehicle): A vehicle model object.
        """

        self.session.add(vehicle)
        self.session.commit()

    def update(self, vehicle: Vehicle) -> None:
        """Update a existent user in the database.

        Parameters:
           model (object): A user model object.
        """

        self.session.commit()

    def delete(self, vehicle: Vehicle) -> None:
        """Delete a vehicle from the database.

            Parameters:
               vehicle (Vehicle): The vehicle model object to be deleted.
            """
        self.session.delete(vehicle)
        self.session.commit()
