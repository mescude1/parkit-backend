"""It contains tests for the database.py module"""

import sqlalchemy


def test_database_init(app):
    """
    GIVEN the init() function
    WHEN init() is called (via the app fixture)
    THEN check sqlalchemy initialization
    """

    from app.database import Base, engine, db_session

    assert isinstance(type(Base), type)
    assert engine.__class__ == sqlalchemy.engine.base.Engine
    assert db_session.__class__ == sqlalchemy.orm.scoping.scoped_session


def test_session_shutdown(app, mocker):
    """
    GIVEN the shutdown_session() function
    WHEN shutdown_session() is called
    THEN check if the session is clean
    """

    from app.database import shutdown_session

    mock_session = mocker.MagicMock()
    mocker.patch('app.database.db_session', mock_session)
    shutdown_session()

    mock_session.remove.assert_called_once()
