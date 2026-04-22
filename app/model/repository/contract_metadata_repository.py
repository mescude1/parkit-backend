"""It contains ContractMetadataRepository class."""

from app.model.contract_metadata import ContractMetadata
from app.model.repository import Repository


class ContractMetadataRepository(Repository):
    """It Contains specific method related to de User
    model to do operation in the database.
    """

    def __init__(self):
        Repository.__init__(self, ContractMetadata)

    def save(self, contract_metadata: ContractMetadata) -> None:
        """Saves a contract_metadata in the database.

        Parameters:
           model (ContractMetadata): A contract_metadata model object.
        """

        self.session.add(contract_metadata)
        self.session.commit()

    def update(self, contract_metadata: ContractMetadata) -> None:
        """Update a existent contract_metadata in the database.

        Parameters:
           model (object): A contract_metadata model object.
        """

        self.session.commit()

    def delete(self, contract_metadata: ContractMetadata) -> None:
        """Delete a contract_metadata from the database.

            Parameters:
               contract_metadata (ContractMetadata): The service model object to be deleted.
            """
        self.session.delete(contract_metadata)
        self.session.commit()
