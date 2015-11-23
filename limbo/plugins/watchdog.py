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
    return watchdog_status(text) or all_watchdog_status(text) or watchdog_log(text)
