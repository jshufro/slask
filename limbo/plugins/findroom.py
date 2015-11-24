"""!findroom (optional floor, nyc2|nyc4, default nyc2) (duration, optional, default 30) (optional meeting start time, default at the next half hour) (optional meeting date, default today): finds available conference rooms in eastern time"""

import simplejson
import requests
import re
import datetime
import pytz
import logging
import parsedatetime


def findroom_response(text):
    utc = pytz.utc
    cal = parsedatetime.Calendar()
    current_dt_utc = datetime.datetime.now()
    current_dt_local = \
        utc.localize(datetime.datetime.now()).astimezone(pytz.timezone('US/Eastern'))
    
    match = re.match(r'!findroom ?(on )?(nyc\d|pdx|sfo)? ?(for )?(\d{2})? ?(minutes )?(.+)?', text, re.IGNORECASE)
    if not match:
        print "Warning failed to match regex to %s" % text
        return False

    # WHAT YEAR IS IT
    hour_fraction = current_dt_local.minute / 60.
    if hour_fraction > 0.5: # we're past the 30 currently
        target_minutes = 60-current_dt_local.minute # add minutes to get to the 00 of the next hour
    else:
        target_minutes = 30-current_dt_local.minute # start at the next :30 otherwise
    
    # print(match)
    # parse args
    
    
    
    floor = match.group(2) or 'nyc4'
    try: 
        datetime_obj, _ = cal.parseDT(datetimeString=match.group(6), tzinfo=pytz.timezone("US/Eastern"))
        # print (match.group(6))
        # print (datetime_obj)
        start_date = datetime_obj.strftime('%Y-%m-%d')
        start_time = datetime_obj.strftime('%H:%M:00')
        
    except (AttributeError, TypeError):
        # print "Did not match stuff"
        start_date = current_dt_local.strftime('%Y-%m-%d')
        start_time = (current_dt_local + datetime.timedelta(minutes=target_minutes)).strftime('%H:%M:00')
    
    duration = match.group(4) or 30

    request = {'mode':'json', 'duration':duration, 'date':start_date, 'time':start_time, 'location':floor}
    result = requests.post('http://mmisiewicz.devnxs.net:7777/get_avail', data=simplejson.dumps(request))
    try:
        result_json = result.json()
    except:
        print request, result.text
        return "Something's wrong with Michael's dev server. Such sadness. It's dark."
    
    if len(result_json['available']) == 0:
        return "NO ROOMS FOR YOU!"
    op = 'Rooms available on %s for %s minutes starting at %s %s\n' % (floor, duration, start_date, start_time)
    op +='\n'.join(result_json['available'])
    return op

if __name__ == '__main__':
    print findroom_response({'body':'!findroom'})
    # print findroom({'body':'!findroom london'})
    # print findroom({'body':'!findroom nyc4'})
    # print findroom({'body':'!findroom nyc4 30'})
    # print findroom({'body':'!findroom nyc4 60'})
    # print findroom({'body':'!findroom nyc2 30 16:00'})
    # print findroom({'body':'!findroom nyc2 30 16:00 2014-11-20'})

def on_message(msg, server):
    text = msg.get("text", "")
    return findroom_response(text)
