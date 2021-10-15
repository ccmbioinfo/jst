
def validate_data(name, obj, variable, _type, choices=None, match=None, required=True):
    if required and variable not in obj:
        return "Variable '%s' not found in '%s' object" % (variable, name)
    elif variable in obj and not isinstance(obj[variable], _type):
        return "Variable '%s' in '%s' object has type '%s', expecting type '%s'" % \
               (variable, name, str(type(obj[variable])), _type)
    elif variable in obj and choices is not None and obj[variable] not in choices:
        return "Variable '%s' in '%s' object has value '%s', which is outside acceptable list of choices [%s]" % \
               (variable, name, obj[variable], ", ".join(choices))


def _validate_job_resources(resources):
    valid_resource_keys = [('mem', str), ('cpu', int), ('walltime', str)]

    expected_keys = [_r[0] for _r in valid_resource_keys]
    if set(resources.keys()) != set(expected_keys):
        return "Variable '%s' has value '%s', which doesn't match expected value '%s'" % \
               ('resources', list(resources.keys()), expected_keys)

    for _key, _type in valid_resource_keys:
        err = validate_data('resources', resources, _key, _type)
        if err:
            return err


def _validate_job_hooks(hooks):
    valid_hook_keys = ['start', 'complete', 'error']
    valid_hook_values = [('url', str, None), ('method', str, ['GET', 'POST']), ('data', dict, None)]

    if set(hooks.keys()) != set(valid_hook_keys):
        return "Variable '%s' has value '%s', which doesn't match expected value '%s'" % \
               ('hooks', list(hooks.keys()), valid_hook_keys)
    for _key in valid_hook_keys:
        err = validate_data('hooks', hooks, _key, dict)
        if err:
            return err

        _hook_value = hooks[_key]
        for _hook_subkey, _hook_type, _choices in valid_hook_values:
            err = validate_data('hooks.'+_key, _hook_value, _hook_subkey, _hook_type, choices=_choices)
            if err:
                return err


def validate_job_format(job):
    valid_systems = ['hpc', 'cheo-ri']
    valid_schedulers = ['torque', 'slurm']
    valid_keys = [
        ('system', str, valid_systems), ('scheduler', str, valid_schedulers),
        ('resources', dict, None), ('script', str, None), ('hooks', dict, None)
    ]

    # Validate higher-level objects
    err = None
    for _key, _type, _choices in valid_keys:
        err = validate_data('root', job, _key, _type, choices=_choices)
        if err: break

        # Validate 'resources' object
        if _key == "resources":
            err = _validate_job_resources(job[_key])

        # Validate 'hooks' object
        if _key == "hooks":
            err = _validate_job_hooks(job[_key])

        if err: break

    return err
