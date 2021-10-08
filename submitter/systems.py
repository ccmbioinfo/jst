from typing import NamedTuple


class ConnDetails(NamedTuple):
    hostname: str
    username: str
    key_filename: str
    script_location: str


def hpc():
    conn_details = ConnDetails(
        username='masgouri',
        hostname='172.20.12.201',
        script_location='/home/masgouri/jobs/',
        key_filename='/keys/hpc',
    )
    submit_cmd = 'qsub'

    return conn_details, submit_cmd

def cheori():
    conn_details = ConnDetails(
        username='pouria',
        hostname='192.168.2.21',
        script_location='/tmp/',
        key_filename='/Users/pouria/.ssh/id_rsa',
    )
    submit_cmd = 'sbatch'

    return conn_details, submit_cmd

def select_system(system):
    conn_details, submit_cmd = ConnDetails, ""
    if system == 'hpc':
        conn_details, submit_cmd = hpc()
    elif system == 'cheo-ri':
        conn_details, submit_cmd = cheori()
    return conn_details, submit_cmd
