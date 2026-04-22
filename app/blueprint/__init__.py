"""Flask HTTP REST API - Campus Parking App."""

import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail

blacklisted_tokens = set()
mail = Mail()


def create_app(test_config: dict = None) -> Flask:
    """Crea y configura la instancia de Flask."""

    app = Flask(__name__, instance_relative_config=True)

    test_config = test_config or {}
    load_config(app, test_config)
    init_instance_folder(app)
    init_database(app)
    init_blueprints(app)
    init_commands(app)
    init_jwt(app)
    mail.init_app(app)

    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

    return app


def load_config(app: Flask, test_config) -> None:
    """Carga la configuracion segun el entorno."""

    if os.environ.get('FLASK_ENV') == 'development' or test_config.get('FLASK_ENV') == 'development':
        app.config.from_object('Backend.app.config.Development')
    elif test_config.get('TESTING'):
        app.config.from_mapping(test_config)
    else:
        app.config.from_object('app.config.Production')


def init_instance_folder(app: Flask) -> None:
    """Asegura que el directorio instance exista."""

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def init_database(app) -> None:
    """Inicializa y conecta la base de datos."""

    from .database import init
    init(app)


def init_blueprints(app: Flask) -> None:
    """Registra los blueprints en la aplicacion."""

    from .blueprint.handlers import register_handler
    register_handler(app)

    from .blueprint import autho, index
    from .blueprint.register import bp_register
    from .blueprint.valet import bp_valet
    from .blueprint.verification import bp_verification

    app.register_blueprint(index.bp)
    app.register_blueprint(autho.bp)
    app.register_blueprint(bp_register)
    app.register_blueprint(bp_valet)
    app.register_blueprint(bp_verification)


def init_commands(app):
    from .commands import register_commands
    register_commands(app)


def init_jwt(app):
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklisted_tokens
