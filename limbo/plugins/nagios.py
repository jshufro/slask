"""!99 problems: Alias for status, checks etl-optimization and cacheserver hosts.
!status (<service>|*)? (<host>|*)?: Get Nagios services that are not OK. * means wildcard.
!downtime <service> <duration(minutes)> <host> <comment>: set nagios downtime
!fakeok <service> <host>: Fake OK result for nagios
"""

import re

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ReadTimeout
import random

from limbo import conf

nagios_user = conf.nagios_user
nagios_pass = conf.nagios_pass

BASE_URL = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?_do_confirm=yes&_transid=-1&_do_actions=yes&actions=yes&filled_in=actions&view_name=service&service={service}&host={host}&output_format=json"
BASE_VIEW_URL = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?_do_confirm=yes&_transid=-1&_do_actions=yes&actions=yes&filled_in=actions&view_name={view_name}&output_format=json"
ZK_WARN_VIEW = "allopt_zk_warn" 
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

def ok_etl_opt_zk_warn(text):
    match = re.match(r"^!fakeokzk\s?", text, re.IGNORECASE)
    if not match:
        return False
    url = BASE_VIEW_URL + FAKE_OK
    url = url.format(view_name=ZK_WARN_VIEW)
    return make_request(url)

def ok_etl_opt_80(text):
    match = re.match(r"^!fakeok80\s?", text, re.IGNORECASE)
    if not match:
        return False
    return fake_ok("!fakeok etl-optimization 80")

def fake_ok(text):
    match = re.match(r"^!fakeok\s+(?P<service>[\w-]+)\s+(?P<host>[\w\-\.]+)\s*$", text, re.IGNORECASE)
    if not match:
        return False
    service = match.group('service')
    host = match.group('host')
    if not service or not host:
        return "All fields required: service, host"
    try:
        hostnumber = int(host)

        if (hostnumber == 3):
            host = "03.cacheserver.prod.nym2"
        elif (hostnumber == 4):
            host = "04.cacheserver.prod.lax1"
        else:
            host = "{}.bm-etl-optimization.prod.lax1".format(host)
    except ValueError:
        pass
    url = BASE_URL + FAKE_OK
    url = url.format(host=host, service=service)
    return make_request(url)

def opt_status(text):
    match = re.match(r"!(99\s?problems|status)$", text)
    if not match:
        return False
    text += " * etl-optimization%7Ccacheserver"
    return status(text)

def status(text):
    match = re.match(r"!(99\s?problems|status) (.*) (.*)$", text)
    if not match:
        return False
    url = "https://multimonitor.nym2.adnxs.net/check_mk/view.py?output_format=python&view_name=allunokayprodservices&st1=on"

    should_check = False

    if match.group(2) and match.group(2) != '*':
        should_check = True
        service = "&service={service}".format(service=match.group(2))
        url += service

    if match.group(3) and match.group(3) != '*':
        should_check = True
        host = "&host={host}".format(host=match.group(3))
        url += host

    if not should_check:
        return "Specify at least one of {host, service}. See !help for more info."

    response = None
    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(nagios_user, nagios_pass),
            verify=False,
            timeout=10)
    except ReadTimeout:
        return "Error: Timed out"

    if not response or response.status_code != 200:
        return "Error"

    data = eval(response.text)
    reply = ''
    for stat in data[1:]:
        reply += "{host}: {service}\tStatus: {status}\n".format(
            host=stat[0],
            status=stat[1],
            service=stat[2])
        if stat[3]:
            reply += "Message: {msg}\n".format(msg=stat[3])
    if not reply:
        r = random.randint(0, 1)
        if (r > 0):
            return "But Goob ain't one"
        else:
            return "But Nagios ain't one"
    return '\n```' + reply + '```'

def on_message(msg, server):
    text = msg.get("text", "")
    return set_downtime(text) or opt_status(text) or ok_etl_opt_80(text) or fake_ok(text) or status(text) or ok_etl_opt_zk_warn(text)
