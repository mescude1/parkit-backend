from sqlalchemy import ForeignKey

from app.database import db


class Service(db.Model):
    """
    Defines the Service model, representing a service record in the database.

    This class is designed to store and manage information related to a service.
    Each service represents an entry associated with a driver, a user, a vehicle,
    a contract, along with various locations and status indicators. It serves as
    a blueprint for mapping the corresponding table in the database and includes
    methods for serializing data into a dictionary format.

    Attributes:
        id (int): The primary identifier for the service.
        driver_id (int): Foreign key referencing the associated driver's ID.
        user_id (int): Foreign key identifying the associated user's ID.
        vehicle_id (int): Foreign key referring to the associated vehicle's ID.
        contract_id (int): Foreign key linking the associated contract's ID.
        parking_location (int): Foreign key indicating the parking location's ID.
        pickup_location (int): Foreign key denoting the pickup location's ID.
        keys_location (int): Foreign key specifying the keys location's ID.
        is_finished (bool): Indicates whether the service is complete.
        created_at (datetime): Timestamp for when the service was created.
        is_deleted (bool): Denotes whether the service is marked as deleted.
    """

    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, ForeignKey('vehicles.id'), nullable=True)
    contract_id = db.Column(db.Integer, ForeignKey('contract_metadata.id'), nullable=True)
    parking_location = db.Column(db.Integer, ForeignKey('user_locations.id'), nullable=True)
    pickup_location = db.Column(db.Integer, ForeignKey('user_locations.id'), nullable=True)
    keys_location = db.Column(db.Integer, ForeignKey('user_locations.id'), nullable=True)
    is_finished = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id,
            'contract_id': self.contract_id,
            'parking_location': self.parking_location,
            'is_finished': self.is_finished,
            'created_at': self.created_at,
            'is_deleted': self.is_deleted
        }
