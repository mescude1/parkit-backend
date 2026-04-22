"""It contains UserRepository class."""

from app.model.user import User
from app.model.repository import Repository


class UserRepository(Repository):
    """Contains specific methods related to the User model."""

    def __init__(self):
        Repository.__init__(self, User)

    def get_by_username(self, username: str) -> User:
        """Retrieve a user from the database by username."""
        return self.session.query(User).filter_by(username=username).first()

    def save(self, user: User) -> None:
        """Saves a user in the database."""
        self.session.add(user)
        self.session.commit()

    def update(self, user: User) -> None:
        """Update an existing user in the database."""
        self.session.commit()

    def authenticate(self, username: str, password: str) -> bool:
        """Check user authenticity by username and password."""
        user = self.get_by_username(username)
        if user and user.authenticate(password):
            return user
        return False

    def is_invalid(self, user: User) -> list:
        """Checks if a given user object is valid.

        Returns:
            list: A list containing field errors, empty if valid.
        """
        invalid = list()

        if not user.username:
            invalid.append({"username": "must be filled"})

        if not user._password_hash:
            invalid.append({"password": "must be filled"})

        # verify if there is another user with the same username
        user_checking = self.get_by_username(user.username)
        if user_checking:
            if (not user.id) or (user.id != user_checking.id):
                invalid.append({"username": "is already in use."})

        if invalid:
            user.remove_session()

        return invalid

    @classmethod
    def get_user_from_token(cls, token):
        pass
