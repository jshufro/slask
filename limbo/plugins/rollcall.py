"""!rollcall: lists all opt-tech members currently active in the room"""

import requests
import sys
import re
from redis import StrictRedis
from limbo import conf

token = 'xoxp-2543006699-3669524994-6723996225-a82588'
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

def on_message(msg, server):
    text = msg.get('text', '')
    match = re.match(r'!rollcall', text, re.IGNORECASE)
    if not match:
        return False

    channel_users = get_users()
    roll_users = REDIS.lrange(ROLLCALL_KEY, 0, -1)

    channel_usernames = []
    for user_id in channel_users:
        channel_usernames.append(get_username(user_id))

    matched_users = filter(lambda x: x in roll_users, channel_usernames)

    if not matched_users:
        return "No one's around right now."

    return "Present: " + ' '.join(sorted(matched_users))


if __name__ == "__main__":
    print on_message({'text': '!summon ' + sys.argv[1]}, None)
