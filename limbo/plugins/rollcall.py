"""!rollcall: lists all opt-tech members currently active in the room"""

import re

import requests
from redis import StrictRedis
from limbo import conf
import os

token = os.environ['SLACK_TOKEN']
optimization_channel = 'C03KM8KEH'
REDIS = StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
ROLLCALL_KEY = "rollcall"

def get_users():
    users_url = 'https://slack.com/api/channels.info?token={0}&channel={1}'.format(token, optimization_channel)
    r = requests.get(users_url)
    return r.json().get('channel').get('members')

def get_username(user_id):
    users_url = 'https://slack.com/api/users.info?token={}&user={}'.format(token, user_id)
    r = requests.get(users_url)
    return r.json().get('user').get('name')

def get_presence(user_id):
    presence_url = 'https://slack.com/api/users.getPresence?token={}&user={}'.format(token, user_id)
    r = requests.get(presence_url)
    return r.json().get('presence') == 'active'


def on_message(msg, server):
    text = msg.get('text', '')
    match = re.match(r'!rollcall', text, re.IGNORECASE)
    if not match:
        return False

    roll_users = REDIS.hgetall(ROLLCALL_KEY)
    channel_usernames = []
    for username, user_id in roll_users.items():
        if get_presence(user_id):
            channel_usernames.append(channel_usernames)

    if not channel_usernames:
        return "No one's around right now."

    return "Present: " + ' '.join(sorted(channel_usernames))