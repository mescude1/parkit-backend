"""This package is Flask HTTP REST API Template that already has the database bootstrap
implemented and also all feature related with the user authentications.

Application features:
    Python 3.13
    Flask
    PEP-8 for code style

This module contains the factory function 'create_app' that is
responsible for initializing the application according
to a previous configuration.
"""


import os

from flask import Flask
from flask_cors import CORS

def create_app(test_config: dict = None) -> Flask:
    """This function is responsible to create a Flask instance according
    a previous setting passed from environment. In that process, it also
    initializes the database source.

    Parameters:
        test_config (dict): settings coming from test environment

    Returns:
        flask.app.Flask: The application instance
    """

    app = Flask(__name__, instance_relative_config=True)

    load_config(app, test_config)

    CORS(app)
    init_instance_folder(app)
    init_database(app)
    init_blueprints(app)
    init_commands(app)
    init_jwt(app)

    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ["access", "refresh"]

    return app


def load_config(app: Flask, test_config) -> None:
    """Load the application's config

    Parameters:
        app (flask.app.Flask): The application instance Flask that'll be running
        test_config (dict):
    """

    test_config = test_config or {}
    env = test_config.get('FLASK_ENV') or os.environ.get('FLASK_ENV', 'production')

    if env == 'development':
        app.config.from_object('app.config.Development')
    else:
        app.config.from_object('app.config.Production')

    if test_config:
        app.config.from_mapping(test_config)


def init_instance_folder(app: Flask) -> None:
    """Ensure the instance folder exists.

    Parameters:
        app (flask.app.Flask): The application instance Flask that'll be running
    """

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def init_database(app) -> None:
    """Responsible for initializing and connecting to the database
    to be used by the application.

    Parameters:
        app (flask.app.Flask): The application instance Flask that'll be running
    """

    from .database import init
    init(app)


def init_blueprints(app: Flask) -> None:
    """Register the blueprint to the application.

    Parameters:
        app (flask.app.Flask): The application instance Flask that'll be running
    """

    # error handlers
    from .blueprint.handlers import register_handler
    register_handler(app)

    from .blueprint import index, autho, profile
    from .blueprint.register import bp_register
    from .blueprint.valet import bp_valet
    from .blueprint.vehicles import bp_vehicles
    from .blueprint.account import bp as bp_account
    from .blueprint.display import bp_display
    from .blueprint.verification import bp_verification
    from .blueprint.device_token import bp_device_token
    from .blueprint.chat import bp_chat
    app.register_blueprint(index.bp)
    app.register_blueprint(autho.bp)
    app.register_blueprint(profile.bp_profile)
    app.register_blueprint(bp_register)
    app.register_blueprint(bp_valet)
    app.register_blueprint(bp_vehicles)
    app.register_blueprint(bp_account)
    app.register_blueprint(bp_display)
    app.register_blueprint(bp_verification)
    app.register_blueprint(bp_device_token)
    app.register_blueprint(bp_chat)


def init_commands(app):
    from .commands import register_commands
    register_commands(app)


def init_jwt(app):
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from app.model.token_blacklist import TokenBlacklist
        return TokenBlacklist.query.filter_by(jti=jwt_payload["jti"]).first() is not None
