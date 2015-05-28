__author__ = "Kevin Hsu (khsu@appnexus.com)"

import requests
import re
import json
from datetime import datetime
import os, json
import conf

username = conf.appnexus_user
password = conf.appnexus_pass
DCS = ('nym1', 'nym2', 'lax1', 'ams1', 'sin1', 'fra1')
URL_BIDDER = 'https://metrics.adnxs.net/render?from=-30minutes&until=now&target=clusters.prod.bidderc.*.budget.age_seconds&format=json'
URL_IMPBUS = 'https://metrics.adnxs.net/render?from=-30minutes&until=now&target=clusters.prod.impbus.*.budget.age_seconds&format=json'

def find_latest_age(metrics):
    i = -1
    dc_age  = {}
    for dc, metric in metrics.iteritems():
        age = None
        while age is None:
            age = metric[i][0]
            i = i - 1
        dc_age[dc] = age
    return dc_age

def fetch_metrics(url):
    metrics = {}
    ret = requests.get(url, auth =(username, password))
    ret = json.loads(ret.content)

    for data in ret:
        dc = data['target'].split('.')[3]
        metrics[dc] = data['datapoints']
    return  metrics

def on_message(msg, server):
    """!budget: show budget age"""
    text = msg.get("text", "")
    reg = re.compile('^!budget(\s(\w+))?', re.IGNORECASE)
    match = reg.match(text)
    if not match:
        return

    url = URL_BIDDER
    if match.group(2):
        if match.group(2).lower() == 'impbus':
            url = URL_IMPBUS
    metrics = fetch_metrics(url)
    dc_age = find_latest_age(metrics)
    return '\n'.join(['%4s: %5d seconds  %s' % (dc, age, '.'* int(age/600)) for dc, age in dc_age.iteritems()])
