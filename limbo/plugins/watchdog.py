"""!doge city: Watchdog info for all hosts
!such status <host>: Watchdog info for host
!watchdog log <host>: tails the watchdog log for that host"""

import subprocess
import re
import requests
import shlex
from requests.auth import HTTPBasicAuth
from limbo import conf


nagios_user = conf.nagios_user
nagios_pass = conf.nagios_pass


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


def watchdog_orphans(body):
    reg = re.compile('!(doge)?([\s|_])?orphans', re.IGNORECASE)
    match = reg.match(body)
    if not match:
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

    output += "Latest version:{}\n".format(max_version)

    if len(version_host_list_map) == 1:
        output += "No orphans!"
    else:
        output += "Orphans:\n"

    for version, host_list in version_host_list_map:
        if version != max_version:
            host_list_str = "\n".join(host_list)
            output += "\nVersion: {v}\nHosts:\n{h}".format(v=version, h=host_list_str)
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


def on_message(msg, server):
    text = msg.get("text", "")
    return watchdog_status(text) or all_watchdog_status(text) or watchdog_orphans(text) or watchdog_log(text)
