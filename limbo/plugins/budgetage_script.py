# -*- coding: utf-8 -*-
"""!budget: show budget age"""

import requests
import re
import json
from limbo import conf

username = conf.appnexus_user
password = conf.appnexus_pass
URL_BIDDER = 'https://metrics.adnxs.net/render?from=-30minutes&until=now&target=clusters.prod.bidderc.*.budget.age_seconds&format=json'
URL_IMPBUS = 'https://metrics.adnxs.net/render?from=-30minutes&until=now&target=clusters.prod.impbus.*.budget.age_seconds&format=json'

def find_latest_age(metrics):
    i = -1
    dc_age = {}
    for dc, metric in metrics.iteritems():
        age = None
        while age is None:
            age = metric[i][0]
            i = i - 1
        dc_age[dc] = age
    return dc_age

def fetch_metrics(url):
    metrics = {}
    ret = requests.get(url, auth=(username, password))
    ret = json.loads(ret.content)

    for data in ret:
        dc = data['target'].split('.')[3]
        metrics[dc] = data['datapoints']
    return metrics

def age_to_string(dc_age):
    return '\n'.join(['%4s: %5d seconds  %s' % (dc, age, '.' * int(age / 600)) for dc, age in dc_age.iteritems()])

def on_message(msg, server):
    text = msg.get("text", "")
    reg = re.compile('!budget', re.IGNORECASE)
    match = reg.match(text)
    if not match:
        return

    return '\n```BIDDER:\n%s \n\nIMPBUS:\n%s \n```' % (
           age_to_string(find_latest_age(fetch_metrics(URL_BIDDER))),
           age_to_string(find_latest_age(fetch_metrics(URL_IMPBUS)))
    )
