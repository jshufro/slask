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
from collections import defaultdict


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
    state_set = set()
    # map of maps {version -> {state -> [(appname, host)]}}
    version_state_host_list_map = defaultdict(lambda: defaultdict(list))
    for i in data:
        # status = i[0]
        host = i[1]
        message = i[2]
        matches = re.finditer(r"(?P<appname>\S*)\[pid:(\S*), version:(?P<version>\S*), state:(?P<state>\S*)]", \
                                message, re.IGNORECASE)
        for match in matches:
            appname = match.group('appname')
            version = match.group('version')
            state = match.group('state')
            state_set.add(state)
            version_state_host_list_map[version][state].append((appname, host))

            if version > max_version:
                max_version = version

    output += "Latest version: {}\n".format(max_version)
    if 'RESTARTING' not in state_set and len(version_state_host_list_map) == 1:
        output += "No orphans!"
    else:
        output += "\n"

    lazy_host_list = orphans_get_lazy_hosts()

    for version, state_host_list_map in sorted(version_state_host_list_map.iteritems(), reverse=True):
        version_output = "\nVersion: {}\n".format(version)
        state_output_list = []
        for state, appname_host_list in sorted(state_host_list_map.iteritems()):
            state_output = "\tState: {}".format(state)
            if version != max_version or state == 'RESTARTING':
                worker_bees = []
                funemployed = []
                for appname, host in appname_host_list:
                    appname_host_str = "\t\t\t{0:25} {1}".format(appname, host)
                    if host in lazy_host_list:
                        funemployed.append(appname_host_str)
                    else:
                        worker_bees.append(appname_host_str)

                init_string = "\t\t\t{0:25} {1}\n".format('Application', 'Host')
                if worker_bees:
                    worker_str = init_string + "\n".join(worker_bees)
                    state_output += "\n\t\tWu-Tang Killah Bees:\n{}".format(worker_str)
                if funemployed:
                    lazy_str = init_string + "\n".join(funemployed)
                    state_output += "\n\t\tLazy Bums:\n{}".format(lazy_str)
                state_output_list.append(state_output)

        if state_output_list:
            output += version_output
            output += "\n".join(state_output_list) + "\n"
    return "```%s```" % output


def on_message(msg, server):
    text = msg.get("text", "")
    return watchdog_status(text) or all_watchdog_status(text) or orphans(text) or watchdog_log(text)
