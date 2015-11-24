"""!rollcall: lists all opt-tech members currently active in the room"""

import requests
import sys
import re
from redis import StrictRedis

token = 'xoxp-2543006699-3669524994-6723996225-a82588'
optimization_channel = 'C03KM8KEH'
REDIS = StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
ROLLCALL_KEY = "rollcall"

def get_users():
    users_url = 'https://slack.com/api/channels.list?token={}&channel={1}'.format(token, optimization_channel)
    r = requests.get(users_url)
    return r.json().get('channel').get('members')

def on_message(msg, server):
    text = msg.get('text', '')
    match = re.match(r'!rollcall', text, re.IGNORECASE)
    if not match:
        return False

    channel_users = get_users()
    roll_users = REDIS.lrange(ROLLCALL_KEY)
    # matched_users = []
    # (channel_users in roll)
    # for user in channel_users:
    #     if user in roll:
    #         matched_users.append(user)

    matched_users = filter(lambda x: x['name'].lower() in roll_users, channel_users)

    if not matched_users:
        return "No one's around right now."

    return "Present: " + ' '.join(sorted(matched_users))


if __name__ == "__main__":
    print on_message({'text': '!summon ' + sys.argv[1]}, None)
