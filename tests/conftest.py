"""This module is responsible to initial configuration of the test. On that,
it creates fixtures to get an applicationinstance and simulates interactions over it.
"""


import collections
import collections.abc
import os
import pytest

# alchemy_mock uses collections.Mapping removed in Python 3.10+
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

from app import create_app

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test.db')
TEST_DB_URI = f'sqlite:///{TEST_DB_PATH}'


def init_db() -> None:
    """Create all tables in the test database."""

    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Delete all rows from every table (SQLite-safe, no DROP needed)."""

    from app.database import Base, engine
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text('PRAGMA foreign_keys = OFF'))
        for table in Base.metadata.tables.values():
            conn.execute(table.delete())
        conn.execute(text('PRAGMA foreign_keys = ON'))
        conn.commit()


def create_test_user() -> None:
    """Creates test user."""

    from app.model import User
    from app.database import db_session
    from datetime import datetime

    user = db_session.query(User).filter_by(username='test').first()

    if not user:
        user = User()
        user.username = 'test'
        user.password_hash = 'test'
        user.name = 'Test'
        user.last_name = 'User'
        user.email = 'test@test.com'
        user.cellphone = '0000000000'
        user.type = 'cliente'
        user.profile_img = 'profile.jpg'
        user.id_img = 'id.jpg'
        user.driver_license_img = 'license.jpg'
        user.contract = 'contract.pdf'
        user.vehicle_type = 'car'
        user.created_at = datetime.utcnow()
        user.is_deleted = False
        user.is_verified = False

        db_session.add(user)
        db_session.commit()


@pytest.fixture
def app(request):
    """ Create a application instance from given settings.

    Parameters:
        request (FixtureRequest): A request for a fixture from a test or fixture function

    Returns:
        flask.app.Flask: The application instance
    """

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DB_URI,
        'JWT_BLACKLIST_ENABLED': True,
        'JWT_BLACKLIST_TOKEN_CHECKS': ['access', 'refresh'],
        'SECRET_KEY': 'dev',
        'JWT_SECRET_KEY': 'dev'
    })

    ctx = app.app_context()
    ctx.push()

    def teardown():
        drop_db()
        ctx.pop()
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    init_db()
    create_test_user()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='function')
def client(app):
    """Create a client with app.test_client() using app fixture."""

    return app.test_client()


@pytest.fixture(scope='function')
def session(app, request):
    """Creates a new database session for a test."""

    from app.database import db_session

    def teardown():
        db_session.remove()

    request.addfinalizer(teardown)
    return db_session


@pytest.fixture(scope='function')
def runner(app):
    """Create a runner with app.test_cli_runner() using app fixture."""

    return app.test_cli_runner()


@pytest.fixture
def auth(app, request):
    """Creates HTTP authorization header with JWT tokens."""

    from flask_jwt_extended import create_access_token, create_refresh_token

    access_token_encoded = create_access_token(identity='test')
    refresh_token_encoded = create_refresh_token(identity='test')

    headers = {
        'access_token': {'Authorization': 'Bearer ' + access_token_encoded},
        'refresh_token': {'Authorization': 'Bearer ' + refresh_token_encoded},
    }

    return headers
