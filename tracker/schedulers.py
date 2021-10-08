
def status_map(status):
    if status == 'Q':
        return 'pending'
    elif status == 'R':
        return 'start'
    elif status == 'C':
        return 'complete'


def check_job_status(ssh, scheduler, job_id):
    exit_code = 0

    cmd, clean_cmd, exitcode_cmd = poll_cmds(scheduler)
    _, res, err = ssh.exec_command('%s %s %s' % (cmd, job_id, clean_cmd))
    job_status = res.read().strip().decode("utf-8")

    status = status_map(job_status)
    if status == 'complete':
        _, res, err = ssh.exec_command('%s %s %s' % (cmd, job_id, exitcode_cmd))
        exit_code = int(res.read().strip().decode("utf-8"))

        if exit_code != 0:
            status = 'error'

    print("Job %s: %s. Exit code: %s" % (job_id, job_status, exit_code))

    return status, exit_code


def poll_cmds(scheduler):
    cmd, clean_cmd, exitcode_cmd = "", "", ""
    if scheduler == 'torque':
        cmd = 'qstat -f'
        clean_cmd = "| grep 'job_state' | awk -F '=' '{print $2}'"
        exitcode_cmd = "| grep 'exit_status' | awk -F '=' '{print $2}'"
    elif scheduler == 'slurm':
        cmd, clean_cmd = 'squeue', "-o %.2t -h"
    return cmd, clean_cmd, exitcode_cmd
