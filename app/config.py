"""This module contains class whose instances will be used to
load the settings according to the running environment."""

import os

from dotenv import load_dotenv


class Default():
    """Class containing the default settings for all environments."""

    DEBUG = False
    TESTING = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail: configuracion base (overrideable via env vars)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False


class Production(Default):
    """Class containing the settings of the production environment."""

    SECRET_KEY = b'p\xa84r!\xb0\x16@"\x840#8n9\xb4'
    JWT_SECRET_KEY = b'p\xa84r!\xb0\x16@"\x840#8n9\xb4'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')


class Development(Default):
    """Class containing the settings of the development environment."""

    load_dotenv()  # loading .env

    DEBUG = True
    SECRET_KEY = 'dev'
    JWT_SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Credenciales de Gmail para desarrollo — cargar desde .env
    # Agregar al archivo .env:
    #   MAIL_USERNAME=tucorreo@gmail.com
    #   MAIL_PASSWORD=tu_app_password_de_gmail
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
