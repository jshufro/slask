"""!doge city: Watchdog info for all hosts
!such status <host>: Watchdog info for host
!watchdog log <host>: tails the watchdog log for that host
!orphans: Shows latest versions, and hosts that do not conform
"""

import subprocess
import re
import requests
import shlex
from requests.auth import HTTPBasicAuth
from limbo import conf


nagios_user = conf.nagios_user
nagios_pass = conf.nagios_pass

DB = 'mysql -A -u%s -p%s -hmysql-budget-slave.prod.adnxs.net -D optimization' % (conf.db_user, conf.db_pass)

def watchdog_status(body):
    reg = re.compile('!such[\s|_]status (.*)', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    host = match.group(1)
    try:
        int(host)
        host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except ValueError:
        pass
    cmd = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s "cat /var/run/watchdog.status"' % host
    stat = subprocess.check_output(cmd, shell=True)
    return stat


def all_watchdog_status(body):
    reg = re.compile('!doge[\s|_]city', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    url = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?service=etl-optimization-watchdog&opthostgroup=&host=&view_name=servicedesc&st0=on&st1=on&st2=on&st3=on&stp=on&output_format=python"
    response = requests.get(url, auth=HTTPBasicAuth(nagios_user, nagios_pass), verify=False)
    data = eval(response.text)
    output = ""
    for i in data:
        output += "Host: {h}\tStatus: {s}\tDoge: {d}\n".format(h=i[1], s=i[0], d=i[2])
    return "```%s```" % output


def watchdog_log(body):
    reg = re.compile('!watchdog log (.*)', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    host = match.group(1)
    try:
        int(host)
        host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except:
        pass
    cmd = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no %s "tail -n 15 /var/log/adnexus/watchdog.log"' % host
    stat = subprocess.check_output(shlex.split(cmd))
    return "\n" + stat


def orphans_get_lazy_hosts():
    query = """select distinct host
            from work_queue_task
            where host not in (select t.host
            from optimization.work_queue_task t
            join work_queue_job_cache jc
            on jc.deleted = 0 and t.job_id = jc.job_id
            WHERE t.status = 'running') order by 1
            ;"""

    command_str = 'echo "' + query + '" | ' + DB
    result = subprocess.check_output(command_str, shell=True)
    if not result:
        return []
    else:
        return result.split('\n')[1:]

def orphans(body):
    if not body.startswith('!orphans'):
        return False

    url = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?service=etl-optimization-watchdog&opthostgroup=&host=&view_name=servicedesc&st0=on&st1=on&st2=on&st3=on&stp=on&output_format=python"
    response = requests.get(url, auth=HTTPBasicAuth(nagios_user, nagios_pass), verify=False)
    data = eval(response.text)
    output = ""
    max_version = ""
    version_host_list_map = {}
    for i in data:
        # status = i[0]
        host = i[1]
        message = i[2]
        match = re.match(r'(.*)version:(?P<version>.*)]:(.*)', message, re.IGNORECASE)
        if not match:
            continue

        version = match.group('version')
        if version not in version_host_list_map:
            version_host_list_map[version] = []
        version_host_list_map[version].append(host)

        if version > max_version:
            max_version = version

    output += "Latest version: {}\n".format(max_version)

    if len(version_host_list_map) == 1:
        output += "No orphans!"
    else:
        output += "\n"

    lazy_host_list = orphans_get_lazy_hosts()

    for version, host_list in version_host_list_map.iteritems():
        if version != max_version:
            worker_bees = []
            funemployed = []
            for host in host_list:
                if host in lazy_host_list:
                    funemployed.append(host)
                else:
                    worker_bees.append(host)

            worker_str = "\n".join(worker_bees)
            lazy_str = "\n".join(funemployed)
            output += "\nVersion: {}".format(version)
            if worker_str:
                output += "\nWu-Tang Killah Bees:\n{}".format(worker_str)
            if lazy_str:
                output += "\nLazy Bums:\n{}".format(lazy_str)
            output += "\n"
    return "```%s```" % output


def on_message(msg, server):
    text = msg.get("text", "")
    return watchdog_status(text) or all_watchdog_status(text) or orphans(text) or watchdog_log(text)
