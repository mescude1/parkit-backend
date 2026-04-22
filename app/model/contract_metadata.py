from sqlalchemy import ForeignKey

from app.database import db


class ContractMetadata(db.Model):
    """
    Represents metadata for a contract stored in the database.

    This class is mapped to the `contract_metadata` table in the database and is
    used to store and retrieve metadata about contracts. It includes information
    such as the contract's URL, the associated user and service IDs, timestamps for
    when it was created and signed, the type of the contract, and a flag indicating
    if it has been deleted. The class also provides a method to represent its data
    as a dictionary.

    Attributes:
        id (int): The unique identifier for the contract metadata.
        contract_url (str): The URL where the contract is stored.
        user_id (int): The identifier of the user associated with the contract.
        signed_at (datetime): The timestamp of when the contract was signed.
        service_id (int, optional): The identifier of the associated service, if any.
        type (str): A string indicating the type of contract.
        created_at (datetime): The timestamp of when the metadata record was created.
        is_deleted (bool): A flag indicating whether the contract metadata record
            has been marked as deleted.
    """

    __tablename__ = 'contract_metadata'

    id = db.Column(db.Integer, primary_key=True)
    contract_url = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    signed_at = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(db.Integer, ForeignKey('services.id'), nullable=True)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'contract_url': self.contract_url,
            'user_id': self.user_id,
            'signed_at': self.signed_at,
            'service_id': self.service_id,
            'type': self.type,
            'created_at': self.created_at
        }
