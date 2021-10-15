import pika
import json
import time
import pickle
import systems
import requests
import schedulers
from config import *
from utils import PersistentDict
from apscheduler.schedulers.background import BackgroundScheduler


# Give container enough time for rabbitmq service to come up (only necessary in dev/testing mode)
time.sleep(10)
sched = BackgroundScheduler()
curr_jobs = PersistentDict('jobs.json')


def run_after_hook(after_hook):
    res = None
    if after_hook['method'] == 'GET':
        res = requests.get(after_hook['url'])
    elif after_hook['method'] == 'POST':
        res = requests.post(after_hook['url'], data=json.dumps(after_hook['data'], indent=4))

    print("After-hook response: %s" % res)

    return res is not None and res.status_code == 200


def poll_jobs():
    for system in curr_jobs:
        conn_details, ssh = systems.connect(system)

        for scheduler in curr_jobs[system]:
            for job in curr_jobs[system][scheduler][:]:
                # TODO: If job is just not found, we should log it and remove script
                status, exit_code = schedulers.check_job_status(ssh, scheduler, job['job_id'])
                if status != job['status']:
                    curr_jobs[system][scheduler]['status'] = status
                    print("New status: '%s'" % status)

                    success = run_after_hook(job['hooks'][status])
                    if success:
                        if status in ['complete', 'error']:
                            print("Job is now over, removing script file")
                            systems.remove_script_file(ssh, job['script_path'])
                            curr_jobs[system][scheduler].remove(job)
                    else:
                        print("Error occurred when running '%s' hook" % status)
                    curr_jobs.update()
        ssh.close()


def callback(ch, method, properties, body):
    message = pickle.loads(body)

    system, scheduler = message['system'], message['scheduler']
    if system not in curr_jobs:
        curr_jobs[system] = {}
    if scheduler not in curr_jobs[system]:
        curr_jobs[system][scheduler] = []
    curr_jobs[system][scheduler].append({
        'status': 'pending',
        'hooks': message['hooks'],
        'job_id': message['job_id'],
        'script_path': message['script_path'],
    })
    print("Job %s added to queue" % message['job_id'])
    curr_jobs.update()

    # Acknowledge completion
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Run 'poll_jobs' function every 30 seconds
sched.add_job(poll_jobs, 'interval', seconds=30)
sched.start()

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

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=receiver_queue_name, on_message_callback=callback)

print('Worker configured, waiting for messages...')
channel.start_consuming()
