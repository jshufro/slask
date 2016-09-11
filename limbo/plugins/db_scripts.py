"""!job cache <failed>: show cached/running jobs <recent failed jobs>
!last[ jobs] [X=5] [handler]: last X scheduled jobs
!scheduler log <querystring> : grep scheduler log
!host <number|host_name|regex> : list tasks running on matching host(s)
!job logs <job_id> : logs for all tasks of this job
!task logs <task_id>: fetch task logs
!tasks [running|completed|failed|queued|killed] <job_id>: task statuses for job
!lazyhost : finds all hosts that are not working on any tasks.
"""

from datetime import datetime, timedelta
import subprocess
import re
from limbo import conf


DB = 'mysql -A -u%s -p%s -hmysql-budget-slave.prod.adnxs.net -D optimization' % (conf.db_user, conf.db_pass)

def get_host_task_pairs(job_id):
    query = """select host, work_task_id
                from work_queue_task
                where job_id = %s;"""

    cmd = 'echo "' + (query % job_id) + '" | ' + DB
    result = subprocess.check_output(cmd, shell=True)
    result_list = result.decode().rstrip().split('\n')

    host_task_pairs = []
    for i in range(1, len(result_list)):
        fields = result_list[i].split('\t')
        tuple = (fields[0], fields[1])
        host_task_pairs.append(tuple)

    return host_task_pairs

def search_job_logs(job_id, search_term):
    host_task_pairs = get_host_task_pairs(job_id)

    response = ""

    for host, task_id in host_task_pairs:
        grep_cmd = "grep '%s' /var/log/adnexus/work_queue_tasks/task_%s" % (search_term, task_id)
        option = "-oStrictHostKeyChecking=no"

        ssh = subprocess.Popen(["ssh", option, host, grep_cmd], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        result = ssh.stdout.readlines()
        if not result:
            result = ssh.stderr.readlines()

        if result:
            response += '\n'.join(result)
        else:
            response += 'Nothing for: %s %s\n' % (host, task_id)

    if response:
        return '```%s```' % response
    else:
        return "No results found."

def job_search(body):
    reg = re.compile('!job_search\s(\d+)\s(.*)', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    job_id = match.group(1)
    search_term = match.group(2)
    return search_job_logs(job_id, search_term)


def job_cache(body):
    query = """select id, job_id, handler, insert_time
                from work_queue_job_cache
                where deleted = 0;"""

    reg = re.compile('^!job[\s|_](cache|\$)\s*((?P<fail>failed))?', re.IGNORECASE)
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


def overspend(body):
    reg = re.compile('!overspend (\d+)', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    update_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    query = """SELECT n.object_type_id, n.object_id,
                    CASE overspend_type
                        WHEN 1 THEN daily_budget
                        ELSE daily_budget_imps
                    END as daily_budget,
                    CASE overspend_type
                        WHEN 1 then delivered
                        ELSE delivered_imps
                    END as delivered,
                    n.over_pct * 100
                FROM budget_daily_overspend_v2 n
                INNER JOIN (
                  SELECT MAX(update_time) AS update_time
                  FROM budget_daily_overspend_v2
                  WHERE update_time >= '{0}'
                ) AS max USING (update_time) order by flag desc limit {1};""".format(update_time, match.group(1))
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
    query = """select host, job_id, work_task_id, handler, t.insert_time, t.start_time,
            timediff(now(), t.start_time) as total
            from work_queue_task t, work_queue_job j
            where t.job_id = j.id and host %s and t.status = 'running'
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
    if host.startswith('regexp'):
        pass
    else:
        host = "like '%s'" % host
    query = query % host
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    if not result:
        return "NO TASKS FOR YOU"
    return "```" + result + "```"


def last_run_jobs(body):
    reg = re.compile('^!last\s+(jobs\s+)?((?P<num>\d+))?\s?((?P<handler>[\w|.]+))?$', re.IGNORECASE)
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
    if result:
        return "```" + result + "```"
    else:
        return "No results"


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


def lazy_host(body):
    query = """SELECT t1.host FROM (SELECT DISTINCT(host) FROM optimization.work_queue_task) t1
            LEFT JOIN (select host, max(insert_time) from optimization.work_queue_task
            WHERE status = 'running' GROUP BY 1) t2
            ON t1.host = t2.host WHERE t2.host IS NULL
            ORDER BY 1
            ;"""

    if not body.startswith('!lazyhost'):
        return False
    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    if not result:
        return "No slackers in these parts."
    return "```" + result + "```"

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
       task_logs, job_logs, grep_scheduler_log, overspend, lazy_host, job_search]


def on_message(msg, server):
    text = msg.get("text", "")
    for fn in ALL:
        response = fn(text)
        if response:
            return response
