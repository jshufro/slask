"""!hashtag <hashtag> : get all messages tagged
!clear <hashtag> : delete that hashtag
!roulette: prints out a random tag
!alltags <query>: all the tags, optionally with a search parameter"""

import re
import cgi
import random
import pytz
import redis
import json
import datetime
from limbo import conf


R = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
PREFIX = 'optbot:'  # redis key namespace for opt-bot
MARKED_KEY_PREFIX = 'opt:'
CB_KEY = 'coldbrew'

# key-value functions

def R_set_response(msg):
    if msg.startswith('!set '):
        args = msg.split()
        if len(args) != 3:
            return 'Error: !set takes 2 parameters'
        R.set(PREFIX + args[1], args[2])
        return 'Success!'

def R_get_response(msg):
    if msg.startswith('!get '):
        args = msg.split()
        if len(args) != 2:
            return 'Error: !get takes 1 parameter'
        return str(R.get(PREFIX + args[1]))

def R_show_response(msg):
    if msg.startswith('!show '):
        args = msg.split()
        if len(args) != 2:
            return 'Error: !show takes 1 parameter'
        response = ''
        link = lambda x, y: '<a href="%s">%s</a>  ' % (cgi.escape(y), x) \
            if y.startswith('http') else '%s' % x
        for k in R.keys(PREFIX + args[1]):
            v = R.get(k)
            response += link(k[len(PREFIX):], v)
            response += '\n'
        return response


# Hashtag functions

def store_marked_msg(msg, server):
    """[#/] picks up any message with a hashtag and stores it under that tag"""
    URL_REGEX = r'(.*)<(http.*)>(.*)'
    text = msg.get("text", "")

    match = re.match(r'(.*) [#](?P<tag>\w+)\s?(.*)$', text, re.IGNORECASE)
    if not match:
        return False

    tag = match.group('tag').lower()
    redis_tag = MARKED_KEY_PREFIX + tag
    message = match.group(0)

    search = re.search(URL_REGEX, message)
    while search:
        message = search.group(1) + search.group(2) + search.group(3)
        search = re.search(URL_REGEX, message)

    try:
        response = json.loads(server.slack.api_call("users.info", user=msg["user"]))
        hashtag_originator = response["user"]["profile"]["real_name"]
        message = message + " -- " + hashtag_originator
    except:
        # something happened when trying to get the user but *shrug*
        pass
    R.rpush(redis_tag, message)
    return "Stored under tag \"{}\"".format(tag)

def get_marked_msg(msg):
    match = re.match(r'!(hashtag )?(.*)', msg, re.IGNORECASE)
    if not match:
        return False
    key = MARKED_KEY_PREFIX + match.group(2).split(" ")[0].lower()
    messages = R.lrange(key, 0, -1)
    return "\n".join(messages)

def clear_hashtag(msg):
    match = re.match(r'!clear (.*)', msg, re.IGNORECASE)
    if not match:
        return False
    key = MARKED_KEY_PREFIX + match.group(1).split(" ")[0].lower()
    return str(R.delete(key))

def get_all_hashtags(msg):
    match = re.match(r'!alltags ?(.*)', msg, re.IGNORECASE)
    if not match:
        return False
    query = '*' + match.group(1) + '*' if match.group(1) else '*'
    keys = R.keys(MARKED_KEY_PREFIX + query)
    return "\n".join(map(lambda x : x.replace(MARKED_KEY_PREFIX, ''), keys))

def roulette(msg):
    if not re.match(r'!roulette', msg, re.IGNORECASE):
        return False

    zhang_prob = random.random()
    if zhang_prob <= 0.3:
        key = MARKED_KEY_PREFIX + "generalazhang"
        messages = R.lrange(key, 0, -1)
        return "\n".join(messages)

    keys = R.keys(MARKED_KEY_PREFIX + '*')
    key = random.choice(keys)
    messages = R.lrange(key, 0, -1)
    return "\n".join(messages)

def coldbrew(msg):
    match = re.match(r'!coldbrew\s?(.*)?', msg, re.IGNORECASE)
    if not match:
        return False

    if (match.group(1)):
        now = datetime.datetime.now(tz=pytz.timezone('America/New_York'))
        R.set(PREFIX + CB_KEY, match.group(1) + " at " + now.strftime("%Y-%m-%d %H:%M %Z"))
        return "Coldbrew status has been set to: " + match.group(1)
    else:
        return R.get(PREFIX + CB_KEY)




ALL = [R_set_response, R_get_response, R_show_response,
       store_marked_msg, get_marked_msg, clear_hashtag,
       get_all_hashtags, roulette, coldbrew]


def on_message(msg, server):
    text = msg.get("text", "")
    for fn in ALL:
        if fn == store_marked_msg:
            response = fn(msg, server)
        else:
            response = fn(text)
        if response:
            return response
