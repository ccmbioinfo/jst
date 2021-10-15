import os
import ssl
import pika
from pathlib import Path


def read_secret(variable, default=''):
    secret_file = Path('/run/secrets/' + variable)
    if secret_file.is_file():
        return secret_file.read_text().replace('\n', '')
    else:
        return os.getenv(variable, default)

def get_rabbitmq_connection(ENV):
    if False: #ENV == 'production':
        context = ssl.create_default_context(
            cafile="/run/secrets/RABBITMQ_CA_CERTIFICATE"
        )
        context.load_cert_chain(
            "/run/secrets/RABBITMQ_CLIENT_CERTIFICATE",
            "/run/secrets/RABBITMQ_CLIENT_KEY"
        )
        ssl_options = pika.SSLOptions(context, "localhost")
    else:
        ssl_options = None

    # Get RABBITMQ auth data
    rabbitmq_host = os.getenv('RABBITMQ_HOST')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT'))
    rabbitmq_user = os.getenv('RABBITMQ_USER')
    rabbitmq_password = read_secret('RABBITMQ_PASSWORD')
    rabbitmq_vhost = os.getenv('RABBITMQ_VHOST', "/")

    return pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password),
        virtual_host=rabbitmq_vhost,
        ssl_options=ssl_options,
        heartbeat=1200,
        blocked_connection_timeout=300
    )


class Config(object):
    """
    The base config. All shared config values are kept here.
    """

    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    GIT_SHA = os.getenv("GIT_SHA")
    API_KEY = os.getenv("API_KEY", "YOUR_SECRET_KEY")

    # Get environment information
    ENV = os.getenv('FLASK_ENV')

    # Get RABBITMQ connection params
    CONNECTION_PARAMS = get_rabbitmq_connection(ENV)

    # Get RABBITMQ queue data
    FORWARDER_QUEUE_NAME = os.getenv('FORWARDER_QUEUE_NAME')


class DevConfig(Config):
    PREFERRED_URL_SCHEME = 'http'


class TestConfig(Config):
    PREFERRED_URL_SCHEME = 'http'


class ProdConfig(Config):
    PREFERRED_URL_SCHEME = 'https'


configs = {
    'testing': TestConfig,
    'development': DevConfig,
    'production': ProdConfig,
}

config = configs[Config.ENV]
