import pika
import uuid
import pickle
import paramiko
from . import systems
from . import parsers
from flask.json import JSONEncoder
from datetime import date, datetime, time
from flask import abort, current_app as app, request, jsonify, make_response


class DateTimeEncoder(JSONEncoder):
    """
    JSONEncoder override for encoding UTC datetimes in ISO format.
    """

    def default(self, obj):

        # handle any variant of date
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()

        # default behaviour
        return JSONEncoder.default(self, obj)


def abort_json(status, description):
    abort(make_response(jsonify({'error': description}), status))


def api_key_required(fn):
    def inner(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')

        if api_key is None:
            app.logger.error("Request header is incomplete")
            abort_json(401, description="Request headers is missing the API key")
        elif api_key != app.config.get("API_KEY"):
            app.logger.error("Provided API key is invalid")
            abort_json(403, description="Provided API key is invalid")
        else:
            return fn(*args, **kwargs)
    return inner


def establish_connection(conn_details: systems.ConnDetails):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(conn_details.hostname, username=conn_details.username, key_filename=conn_details.key_filename)

    return ssh


def publish_to_queue(payload):
    connection_params = app.config.get("CONNECTION_PARAMS")
    forwarder_queue_name = app.config.get("FORWARDER_QUEUE_NAME")

    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=forwarder_queue_name)

        channel.basic_publish(exchange="", routing_key=forwarder_queue_name, body=pickle.dumps(payload))
        channel.close()
    except Exception as e:
        return str(e)


def submit_job(job):
    script = job['script']
    conn_details, _ = systems.select_system(job['system'])
    resource_query, submit_cmd = parsers.parse_resource_query(job['scheduler'], job['resources'])

    payload, err_msg = None, None
    ssh = establish_connection(conn_details)
    filename = conn_details.script_location + str(uuid.uuid4()) + ".sh"

    # Transfer file to scheduler system
    _, res, err = ssh.exec_command('echo "%s" > %s' % (script, filename))
    if res.channel.recv_exit_status() != 0:
        err_msg = "Error occurred attempting to write file to server, skipping"
    else:
        # Submit job to scheduler
        _, res, err = ssh.exec_command('%s %s %s' % (submit_cmd, resource_query, filename))
        if res.channel.recv_exit_status() != 0:
            err_msg = "Error occurred submitting job, skipping"
        else:
            job_id = res.read().rsplit()[0].decode("utf-8")

            # Prepare resultant body with job_id & after-hook
            payload = {
                'job_id': job_id,
                'script_path': filename,
                'hooks': job['hooks'],
                'system': job['system'],
                'scheduler': job['scheduler']
            }

            err_msg = publish_to_queue(payload)
    ssh.close()

    # If an error had occurred, abort with 500 status
    if err_msg:
        abort_json(500, description=err_msg)

    return payload
