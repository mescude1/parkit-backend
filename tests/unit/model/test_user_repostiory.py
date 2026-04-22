"""Tests for the UserRepository class"""

import sqlalchemy
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

from ...util import get_unique_username


def _make_user(username=None, password=None):
    from app.model.user import User
    user = User()
    if username is not None:
        user.username = username
    if password is not None:
        user.password_hash = password
    return user


def test_create_new_user_repository(app):
    """
    GIVEN the UserRepository class
    WHEN a new UserRepository is created
    THEN check the UserRepository and the SQLAlchemy session instances
    """
    from app.model import UserRepository
    user_repository = UserRepository()

    assert isinstance(user_repository, UserRepository)
    assert isinstance(user_repository.session, sqlalchemy.orm.scoping.scoped_session)


def test_the_get_by_username_method_of_user_repository(app):
    """
    GIVEN the UserRepository class
    WHEN the method get_by_username(username) is called
    THEN check the user object returned
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    username = get_unique_username()
    password = '123'
    user = _make_user(username, password)
    user_repository.session.add(user)
    user_repository.session.commit()

    result = user_repository.get_by_username(username)
    assert result.username == username
    assert result.authenticate(password)
    assert str(result) == '<User %r>' % username


def test_the_save_method_of_user_repository(app):
    """
    GIVEN the UserRepository class
    WHEN the method save(user) is called
    THEN check session method calls and user data
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    username = get_unique_username()
    password = '123'
    user = _make_user(username, password)
    user_repository.save(user)

    user_repository.session.add.assert_called_once_with(user)
    user_repository.session.commit.assert_called_once_with()
    assert user.username == username
    assert user.authenticate(password)


def test_the_update_method_of_user_repository(app):
    """
    GIVEN the UserRepository class
    WHEN the method update(user) is called
    THEN check session method calls and user data
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user(get_unique_username(), '123')
    user_repository.session.add(user)
    user_repository.session.commit()

    username_edited = get_unique_username()
    user.username = username_edited
    user.password_hash = '1234'
    user_repository.update(user)

    assert user.username == username_edited
    assert user.authenticate('1234')


def test_the_authenticate_method_of_user_repository(app):
    """
    GIVEN the UserRepository class
    WHEN the method authenticate(username, password) is called
    THEN check the method return
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user(get_unique_username(), '123')
    user_repository.session.add(user)
    user_repository.session.commit()

    # correct data
    assert user_repository.authenticate(user.username, '123')
    # wrong password
    assert not user_repository.authenticate(user.username, '1234')


def test_the_is_invalid_method_of_user_repository_with_correct_data(app):
    """
    GIVEN the UserRepository class
    WHEN the method is_invalid(user) is called with a valid user
    THEN check it returns empty list
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user(get_unique_username(), '123')
    assert not user_repository.is_invalid(user)


def test_the_is_invalid_method_of_user_repository_with_existent_user(app):
    """
    GIVEN an existing user being edited
    WHEN is_invalid is called
    THEN it should not flag username collision on the same user
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user('test', '123')
    user.id = 1
    user_repository.session.add(user)
    user_repository.session.commit()

    user.username = 'test_edited'
    user.password_hash = '1234'
    assert not user_repository.is_invalid(user)


def test_the_is_invalid_method_of_user_repository_with_username_already_in_use(app):
    """
    GIVEN a new user with a duplicate username
    WHEN is_invalid is called
    THEN it should return a username-in-use error
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    existing = _make_user('test', '123')
    existing.id = 1
    user_repository.session.add(existing)
    user_repository.session.commit()

    new_user = _make_user('test', '123')
    is_invalid = user_repository.is_invalid(new_user)
    assert is_invalid
    assert {"username": "is already in use."} in is_invalid


def test_the_is_invalid_method_of_user_repository_missing_password(app):
    """
    GIVEN a user with no password set
    WHEN is_invalid is called
    THEN it should return a password-must-be-filled error
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user(username='test')
    is_invalid = user_repository.is_invalid(user)
    assert is_invalid
    assert {"password": "must be filled"} in is_invalid


def test_the_is_invalid_method_of_user_repository_missing_username(app):
    """
    GIVEN a user with no username set
    WHEN is_invalid is called
    THEN it should return a username-must-be-filled error
    """
    from app.model import UserRepository

    user_repository = UserRepository()
    user_repository.session = UnifiedAlchemyMagicMock()

    user = _make_user(password='123')
    is_invalid = user_repository.is_invalid(user)
    assert is_invalid
    assert {"username": "must be filled"} in is_invalid
