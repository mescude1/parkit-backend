"""Tests for the User model"""


from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from ...util import get_unique_username


def test_create_new_user(app):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, password auth, serialization and string representation
    """

    username = get_unique_username()
    password = '123'

    from app.model.user import User

    session = UnifiedAlchemyMagicMock()
    user = User()
    user.username = username
    user.password_hash = password
    session.add(user)
    session.commit()

    query = session.query(User).first()
    assert query.username == username
    assert query.authenticate(password)
    assert query.to_dict()['username'] == username
    assert str(query) == '<User %r>' % username
