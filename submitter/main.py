import pika
import time
import uuid
import pickle
import parsers
import systems
import paramiko
from config import *


# Give container enough time for rabbitmq service to come up (only necessary in dev/testing mode)
time.sleep(10)


def callback(ch, method, properties, body):
    message = pickle.loads(body)

    script = message['script']
    conn_details, _ = systems.select_system(message['system'])
    resource_query, submit_cmd = parsers.parse_resource_query(message['scheduler'], message['resources'])

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(conn_details.hostname, username=conn_details.username, key_filename=conn_details.key_filename)

    # Transfer file to scheduler system
    filename = conn_details.script_location + str(uuid.uuid4()) + ".sh"    # Prepend script location?
    _, res, err = ssh.exec_command('echo "%s" > %s' % (script, filename))
    if res.channel.recv_exit_status() != 0:
        print("Error occurred attempting to write file to server, skipping")
    else:
        # Submit job to scheduler
        _, res, err = ssh.exec_command('%s %s %s' % (submit_cmd, resource_query, filename))
        if res.channel.recv_exit_status() != 0:
            print("Error occurred submitting job, skipping")
        else:
            job_id = res.read().rsplit()[0].decode("utf-8")

            # Prepare resultant body with job_id & after-hook
            payload = {
                'job_id': job_id,
                'script_path': filename,
                'hooks': message['hooks'],
                'system': message['system'],
                'scheduler': message['scheduler']
            }
            channel.basic_publish(exchange="", routing_key=forwarder_queue_name, body=pickle.dumps(payload))
            print(' Published:', str(payload['job_id']))
    ssh.close()

    # Acknowledge completion
    ch.basic_ack(delivery_tag=method.delivery_tag)



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

channel.queue_declare(queue=receiver_queue_name)
channel.queue_declare(queue=forwarder_queue_name)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=receiver_queue_name, on_message_callback=callback)

print('Worker configured, waiting for messages...')
channel.start_consuming()



msgFormat = {
    'system': ['hpc', 'cheo-ri'],
    'scheduler': ['torque', 'slurm'],
    'resources': {
        'mem': '2gb',
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
    'job_id': '',
    'script_path': '',
    'after_hook': {
        'url': '',
        'method': ['GET', 'POST'],
        'data': {}
    }
}
