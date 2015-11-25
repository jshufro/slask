"""!99 problems : all etl opt nagios services that are not OK
!downtime <service> <duration(minutes)> <host> <comment>: set nagios downtime
!fake_ok <service> <host>: Fake OK result
"""

import re
import requests
from requests.auth import HTTPBasicAuth

from limbo import conf
nagios_user = conf.nagios_user
nagios_pass = conf.nagios_pass

BASE_URL = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?_do_confirm=yes&_transid=-1&_do_actions=yes&actions=yes&filled_in=actions&view_name=service&service={service}&host={host}&output_format=json"
FAKE_OK = "&_fake_0=OK"
DOWNTIME = "&_down_from_now=From+now+for&_down_minutes={dur}&_down_comment={comment}"

def make_request(url):
    response = requests.get(
        url,
        auth=HTTPBasicAuth(nagios_user, nagios_pass),
        verify=False)
    if response.status_code != 200:
        return "Error"
    # For some reason this URL does not return nice json...
    if response.content.startswith("MESSAGE: Successfully sent 1 commands."):
        return "Success"
    else:
        return "Problem - look at check_mk"

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
    url = BASE_URL + DOWNTIME
    url = url.format(host=host, service=service, dur=duration, comment=comment)
    return make_request(url)

def fake_ok(text):
    match = re.match(r"^!fake_ok\s+(?P<service>[\w-]+)\s+(?P<host>[\w\-\.]+)\s*$", text, re.IGNORECASE)
    if not match:
        return False
    service = match.group('service')
    host = match.group('host')
    if not service or not host:
        return "All fields required: service, host"
    try:
        int(host)
        host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except ValueError:
        pass
    url = BASE_URL + FAKE_OK
    url = url.format(host=host, service=service)
    return make_request(url)

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
    return set_downtime(text) or opt_status(text) or fake_ok(text)
