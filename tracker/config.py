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

# Get environment information
environment = os.getenv('ENVIRONMENT')

# Get RABBITMQ auth data
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT'))
rabbitmq_user = os.getenv('RABBITMQ_USER')
rabbitmq_password = read_secret('RABBITMQ_PASSWORD')
rabbitmq_vhost = os.getenv('RABBITMQ_VHOST', "/")

# Get RABBITMQ queue data
receiver_queue_name = os.getenv('RECEIVER_QUEUE_NAME')

if environment in ['production', 'dev']:
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
