"""!99 problems : all etl opt nagios services that are not OK
!downtime <service> <duration(minutes)> <host> <comment>: set nagios downtime"""

import re
import requests
from requests.auth import HTTPBasicAuth

from limbo import conf
nagios_user = conf.nagios_user
nagios_pass = conf.nagios_pass

def set_downtime(text):
    match = re.match(r"^!downtime\s+(?P<service>[\w-]+)\s+(?P<dur>\d+)\s*(?P<host>[\w\-\.]+)\s*(?P<comment>.*)\s*$", text, re.IGNORECASE)
    if not match:
        return False
    service = match.group('service')
    duration = match.group('dur')
    host = match.group('host')
    comment = match.group('comment')
    if not service or not duration or not host or not comment:
        return "All fields required: service, duration, host, comment"
    try:
        int(host)
        host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except ValueError:
        pass
    url = \
    "https://multimonitor.nym2.adnxs.net/check_mk/view.py?_do_confirm=yes&_transid=-1&_do_actions=yes&actions=yes&host={host}&view_name=service&site=prod-lax1&service={service}&_cusnot_comment=TEST&_ack_comment=&_comment=&_down_from_date=2014-03-30&_down_from_time=04%3A20&_down_to_date=2014-03-30&_down_to_time=06%3A20&_down_from_now=From+now+for&_down_minutes={dur}&_down_duration=02%3A00&_down_comment={comment}&output_format=json"
    url = url.format(host=host, service=service, dur=duration, comment=comment)
    response = requests.get(
        url,
        auth=HTTPBasicAuth(nagios_user, nagios_pass),
        verify=False)
    if response.status_code != 200:
        return "Error"
    # For some reason this URL does not return nice json...
    status = response.content.split('\n')[0]
    if re.compile(".*successfully.*", re.IGNORECASE).match(status):
        return "Downtime set"
    else:
        return "Problem - look at check_mk"


def opt_status(text):
    match = re.match(r"!99 problems\s*$", text)
    if not match:
        return False
    url = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?service=etl-optimization&host=.%2A%5C.prod%5C..%2A&view_name=allprodservices&output_format=python"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(nagios_user, nagios_pass),
        verify=False)
    if response.status_code != 200:
        return "Error"
    data = eval(response.text)
    reply = ''
    for stat in data[1:]:
        if stat[0] != "OK":
            reply += "{host}: {service}\tStatus: {status}\tMessage: {msg}\n".format(
                host=stat[-1],
                service=stat[0],
                status=stat[1],
                msg=stat[2])
    if not reply:
        return "But Nagios ain't one"
    return '\n```' + reply + '```'


def on_message(msg, server):
    text = msg.get("text", "")
    return set_downtime(text) or opt_status(text)
