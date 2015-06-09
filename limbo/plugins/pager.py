import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import conf


username = conf.appnexus_user
password = conf.appnexus_pass
URL = 'https://corpwiki.appnexus.com/display/optimization/Optimization+Engineering+Pager+Rotation'

def pager_response(text):
    """!oncall|!pager (add "link" for url to pager rotation page)"""
    match = re.match('!oncall|!pager', text, re.IGNORECASE)
    if not match:
        return False

    if "link" in match.string:
        return "https://corpwiki.appnexus.com/x/xxsaAQ"
    r = requests.get(URL, auth=(username, password), verify=False)
    soup = BeautifulSoup(r.text)
    tables = soup.find_all('table', 'confluenceTable')
    table_call = tables[0].find_all('td')
    list_call = [i.text for i in table_call]
    reg = re.compile("(\d+)\D+(\d+)\D+(\d+)\D+(\d+)")
    def time_range(t):
        month = datetime.now().month
        day = datetime.now().day
        return (int(t[0]) < month <=int(t[2]) and int(t[3]) >= day) \
            or (int(t[0]) <= month < int(t[2]) and int(t[1]) <= day) \
            or (int(t[0]) <= month <= int(t[2]) and (int(t[3]) >= day >= int(t[1])))

    response = None
    for i in range(0, len(list_call), 3):
        match = reg.match(list_call[i])
        if time_range(match.groups()):
            response = "Primary: {}, Secondary: {}".format(list_call[i+1], list_call[i+2])
    return response or "Not Found"

def on_message(msg, server):
    text = msg.get("text", "")
    return pager_response(text)

