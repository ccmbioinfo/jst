
default_resources = {
    'cpu': '1',
    'mem': '2gb',
    'walltime': '24:00:00'
}

def torque(resource_requests):
    resources = {
        'mem': resource_requests.get('mem', default_resources['mem']),
        'vmem': resource_requests.get('mem', default_resources['mem']),
        'nodes=1:ppn': resource_requests.get('cpu', default_resources['cpu']),
        'walltime': resource_requests.get('walltime', default_resources['walltime'])
    }

    resource_query = "-l "
    for k, v in resources.items():
        resource_query += "%s=%s," % (k, v)
    resource_query = resource_query[:-1]        # Get rid of trailing comma

    return resource_query

def slurm(resource_requests):
    resources = {
        '--mem': resource_requests.get('mem', default_resources['mem']),
        '-c': resource_requests.get('cpu', default_resources['cpu']),
        '-t': resource_requests.get('walltime', default_resources['walltime'])
    }

    resource_query = ""
    for k, v in resources.items():
        resource_query += "%s %s " % (k, v)
    resource_query = resource_query[:-1]  # Get rid of trailing space

    return resource_query

def parse_resource_query(scheduler, resource_query):
    if scheduler == 'torque':
        return torque(resource_query), 'qsub'
    elif scheduler == 'slurm':
        return slurm(resource_query), 'sbatch'
