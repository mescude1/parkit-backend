"""This module provides means to perform operations on the database
using the SQLAlchemy library."""


from flask import Flask
from flask_migrate import Migrate

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

engine = None
db_session = None
Base = None

db = SQLAlchemy()


def init(app: Flask) -> None:
    """This function initialize the SQLAlchemy ORM, providing a session
    and command line to create the tables in the database.

    Parameters:
        app (flask.app.Flask): The application instance.
    """

    global Base, engine, db_session
    if engine is not None:
        engine.dispose()

    if app.testing:
        from sqlalchemy.pool import NullPool
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], poolclass=NullPool)
    else:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base = db.Model

    # creating a new session
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))

    # The declarative extension in SQLAlchemy allows to define
    # tables and models in one go, that is in the same class

    db.init_app(app)

    # print(Base.query)
    # attach the shutdown_session function to be execute when a request ended.
    app.teardown_appcontext(shutdown_session)

    # Using Flask-Migrate as the handler for database migration.
    Migrate(app, db)


def shutdown_session(exception=None) -> None:
    """Remove the session by send it back to the pool."""

    db_session.remove()
