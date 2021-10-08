import paramiko
from typing import NamedTuple


class ConnDetails(NamedTuple):
    hostname: str
    username: str
    key_filename: str
    script_location: str


def hpc():
    return ConnDetails(
        username='masgouri',
        hostname='172.20.12.201',
        script_location='/home/masgouri/jobs/',
        key_filename='/keys/hpc',
    )

def cheori():
    return ConnDetails(
        username='pouria',
        hostname='192.168.2.21',
        script_location='/tmp/',
        key_filename='/Users/pouria/.ssh/id_rsa',
    )

def select_system(system):
    conn_details = ConnDetails
    if system == 'hpc':
        conn_details = hpc()
    elif system == 'cheo-ri':
        conn_details = cheori()
    return conn_details

def connect(system):
    conn_details = select_system(system)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(conn_details.hostname, username=conn_details.username, key_filename=conn_details.key_filename)

    return conn_details, ssh

def remove_script_file(ssh, script_path):
    # Remove file off of server
    _, res, err = ssh.exec_command('rm %s' % script_path)

    return err
