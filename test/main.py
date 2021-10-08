import pika
import time
import pickle
from config import *


# Give container enough time for rabbitmq service to come up (only necessary in dev/testing mode)
time.sleep(10)

# Connect to RabbitMQ
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=credentials,
        virtual_host=rabbitmq_vhost,
        ssl_options=ssl_options,
        heartbeat=1200,
        blocked_connection_timeout=300
    )
)
channel = connection.channel()

channel.queue_declare(queue=forwarder_queue_name)



msgFormat = {
    'system': ['hpc', 'cheo-ri'],
    'scheduler': ['torque', 'slurm'],
    'resources': {
        'mem': 0,
        'cpu': 0,
        'walltime': '',
    },
    'script': '',
    'after_hook': {
        'url': '',
        'method': ['GET', 'POST'],
        'data': {}
    }
}

statusTrackerFormat = {
    'system': ['hpc', 'cheo-ri'],
    'scheduler': ['torque', 'slurm'],
    'job-id': '',
    'script_path': '',
    'after-hook': {
        'url': '',
        'method': ['GET', 'POST'],
        'data': {}
    }
}


file_info = open("test.sh", "r")
script = file_info.read()

message = {
    'system': 'hpc',
    'scheduler': 'torque',
    'resources': {
        'mem': '4gb',
        'cpu': 1,
        'walltime': '3:00:00',
    },
    'script': script,
    'hooks': {
        'start': {
            'url': 'https://google.com',
            'method': 'GET',
            'data': {}
        },
        'complete': {
            'url': 'https://google.com',
            'method': 'GET',
            'data': {}
        },
        'error': {
            'url': 'https://google.com',
            'method': 'GET',
            'data': {}
        }
    }
}

channel.basic_publish(exchange="", routing_key=forwarder_queue_name, body=pickle.dumps(message))
print(' Published:', str(message))
