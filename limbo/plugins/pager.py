import re
import urllib2
import json

def pager_response(text):
    """!oncall|!pager (add "link" for url to pager rotation page)"""
    match = re.match('!oncall|!pager', text, re.IGNORECASE)
    if not match:
        return False

    if "link" in match.string:
        return "https://corpwiki.appnexus.com/x/xxsaAQ"
    return maestro_pager_response() or "Not Found"
    # r = requests.get(URL, auth=(username, password), verify=False)
    # soup = BeautifulSoup(r.text)
    # tables = soup.find_all('table', 'confluenceTable')
    # table_call = tables[0].find_all('td')
    # list_call = [i.text for i in table_call]
    # reg = re.compile("(\d+)\D+(\d+)\D+(\d+)\D+(\d+)")
    # def time_range(t):
    #     month = datetime.now().month
    #     day = datetime.now().day
    #     return (int(t[0]) < month <=int(t[2]) and int(t[3]) >= day) \
    #         or (int(t[0]) <= month < int(t[2]) and int(t[1]) <= day) \
    #         or (int(t[0]) <= month <= int(t[2]) and (int(t[3]) >= day >= int(t[1])))
    #
    # response = None
    # for i in range(0, len(list_call), 3):
    #     match = reg.match(list_call[i])
    #     if time_range(match.groups()):
    #         response = "Primary: {}, Secondary: {}".format(list_call[i+1], list_call[i+2])
    # return response or "Not Found"

# maestro pager code borrowed from data-bot.

def __join_oncall_info(user_infos):
    """ does the joining across the rseponse from maestro3's usergroup map service
        and the timeperiods service, returning a tuple3 of (username, timeperiod_name, hours)
        where hours are on call for day_of_week. If hours is null or the user is deleted
        an entry is not returned day_of_week is expected to be lower case"""
    results = []
    for user_info in user_infos:
        results.append(user_info['username'])

        # if not user_info['deleted']:
        #     # XXX: ignoring out of bounds for now
        #     period = periods[user_info['nagios_timeperiod_id']]
        #     on_call_timerange = period[day_of_week]
        #     if on_call_timerange:
        #         results.append((user_info['username'], period['timeperiod_name'], on_call_timerange))
    return results

# def __get_timeperiods_dict():
#     timeperiods_resp = urllib2.urlopen('http://maestro3-api.adnxs.net/nagios-timeperiod').read()
#     periods = {}
#     for period in json.loads(timeperiods_resp)['response']['nagios_timeperiods']:
#         periods[period['id']] = period
#     return periods

def maestro_pager_response():
    # periods = __get_timeperiods_dict()
    # day_of_week = datetime.now().strftime("%A").lower()

    on_pager_resp = urllib2.urlopen('http://maestro3-api.adnxs.net/nagios-usergroup-map?nagios_usergroup_id=20&pager=1').read()
    on_pagers = __join_oncall_info(json.loads(on_pager_resp)['response']['nagios_usergroup_maps'])

    on_escalation_resp = urllib2.urlopen('http://maestro3-api.adnxs.net/nagios-usergroup-map?nagios_usergroup_id=20&escalation=1').read()
    on_escalations = __join_oncall_info(json.loads(on_escalation_resp)['response']['nagios_usergroup_maps'])

    on_pager_section = ','.join([' %s' % on_pager for on_pager in on_pagers])
    on_escalation_section = ','.join([' %s' % on_escalation for on_escalation in on_escalations])

    reply = '```Primary:%s\nSecondary:%s```' % (on_pager_section, on_escalation_section)
    return reply

def on_message(msg, server):
    text = msg.get("text", "")
    return pager_response(text)

