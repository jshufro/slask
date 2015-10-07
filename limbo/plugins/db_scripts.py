"""!job cache <failed>: show cached/running jobs <recent failed jobs>
!last[ jobs] [X=5] [handler]: last X scheduled jobs
!scheduler log <querystring> : grep scheduler log
!host <number|host_name> : list tasks running on host
!job logs <job_id> : logs for all tasks of this job
!task logs <task_id>: fetch task logs
!tasks [running|completed|failed|queued|killed] <job_id>: task statuses for job"""

import subprocess
import re
import conf


DB = 'mysql -A -u%s -p%s -hmysql-budget-slave.prod.adnxs.net -D optimization' % (conf.db_user, conf.db_pass)


def job_cache(body):
    query = """select id, job_id, handler, insert_time
                from work_queue_job_cache
                where deleted = 0;"""

    reg = re.compile('^!job[\s|_]cache\s*((?P<fail>failed))?', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    if match.group('fail'):
        query = """SELECT id as job_id, handler, insert_time, status
                    FROM work_queue_job
                    WHERE status = 'failed' and insert_time >= (now() - interval 90 minute)
                    ORDER BY insert_time desc """
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    return "```" + result + "```"


def tasks(body):
    query = """select work_task_id, host, status, insert_time, start_time,
                completion_time, if(status = 'completed', timediff(completion_time,
                start_time), timediff(now(), start_time)) as total
                from work_queue_task
                where job_id = %s;"""

    exp = re.compile(r'^!tasks\s+((?P<type>\w+)\s+)?(?P<id>\d+)\s*$')
    match = exp.match(body.lower())
    if match:
        states = ('queued', 'running', 'failed', 'killed', 'completed')
        type_ = match.group('type')
        if type_ not in states:
            type_ = None
        if type_ is not None:
            query = query[:-1] + " and status = '%s';" % type_

        command_str = 'echo "' + query % match.group('id') + '" | ' + DB
        result = subprocess.check_output(command_str, shell=True)
        return "```" + result + "```"


def host_tasks(body):
    query = """select job_id, work_task_id, handler, t.insert_time, t.start_time,
            timediff(now(), t.start_time) as total
            from work_queue_task t, work_queue_job j
            where t.job_id = j.id and host = '%s' and t.status = 'running'
            and t.insert_time >= now() - interval 1 day;"""

    exp = re.compile('!host (.*)', re.IGNORECASE)
    match = exp.match(body.lower())
    if not match:
        return False
    host = match.group(1)
    try:
        int(host)
        host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except ValueError:
        pass
    query = query % host
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    if not result:
        return "NO TASKS FOR YOU"
    return "```" + result + "```"


def last_run_jobs(body):
    reg = re.compile('^!last\s+(jobs\s+)?((?P<num>\d+))?\s?((?P<handler>\w+))?$', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    # default to 5 entries (can change this...)
    num = int(match.group('num')) if match.group('num') else 5
    # see if specific job type
    handler = match.group('handler') or ''

    query = """SELECT id as job_id, handler, status, insert_time, start_time,
                    completion_time,
                    IF(completion_time <> '0000-00-00 00:00:00',
                        timediff(completion_time, start_time),
                        'ITS RUNNING FOOL') as run_time
               FROM work_queue_job
               WHERE handler like '%{}%'
               ORDER BY insert_time desc
               LIMIT {}""".format(handler, num)

    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    return "```" + result + "```"


def host_for_task(task):
    query = "SELECT host FROM work_queue_task WHERE work_task_id = %s" % task
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    return result.split()[-1]


def get_task_log(task_id):
    url = "http://analytics.prod.adnxs.net/work_queue/task_logs/%s" % task_id
    return url


def task_logs(body):
    reg = re.compile('!task[\s|_]logs (.*)', re.IGNORECASE)
    match = reg.match(body)
    if match:
        task_id = match.group(1)
        return get_task_log(task_id)


def tasks_for_job(job_id):
    query = """SELECT work_task_id FROM work_queue_task where job_id = {}""".format(job_id)
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    return result.split('\n')[1:-1]


def job_logs(body):
    reg = re.compile("!job logs (.*)", re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    job_id = int(match.group(1))
    task_info = tasks_for_job(job_id)
    urls = []
    for task_id in task_info:
        url = get_task_log(task_id)
        urls.append(task_id + ": " + url)
    return "```" + "\n".join(urls) + "```"


def grep_scheduler_log(body):
    reg = re.compile('!scheduler log (.*)', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    host = '30.bm-etl-optimization.prod.lax1'
    search = match.group(1)
    if not search:
        return "Please enter a search term"
    cmd = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {} "grep -i {} /var/log/adnexus/scheduler.log" '.format(host, search)
    cmd += " | /home/apando/utils/hpaste "
    url = subprocess.check_output(cmd, shell=True)
    return "```" + url.replace('7777', '7777/raw') + "```"


ALL = [job_cache, tasks, host_tasks, last_run_jobs,
       task_logs, job_logs, grep_scheduler_log]


def on_message(msg, server):
    text = msg.get("text", "")
    for fn in ALL:
        response = fn(text)
        if response:
            return response
