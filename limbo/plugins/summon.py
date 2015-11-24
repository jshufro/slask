import requests
import sys
import re
import os
from limbo import conf


token = os.environ['SLACK_TOKEN']
optimization_channel = 'C03KM8KEH'


def get_users():
    users_url = 'https://slack.com/api/users.list?token={}'.format(token)
    r = requests.get(users_url)
    return r.json().get('members')


def on_message(msg, server):
    body = msg.get('text', '').lower()
    match = re.match(r'!summon\s(.*)', body, re.IGNORECASE)
    if not match:
        return False

    user = match.group(1).split()[0].strip('<').strip('>').strip('@').strip(':')
    if not match:
        return False

    users = get_users()
    matched_users = filter(lambda x: x['id'].lower() == user, users)

    if not matched_users:
        email = '{}@appnexus.com'.format(user)
        matched_users = filter(lambda x: x['profile'].get('email') == email, users)

    if not matched_users:
        return "Could not find user"

    user = matched_users[0]
    user_id = user.get('id')
    invite_url = 'https://slack.com/api/channels.invite?token={0}&channel={1}&user={2}'.format(token, optimization_channel, user_id)
    r = requests.get(invite_url)
    if 'error' in r.json():
        return "Error summoning this user. Try again, novice summoner."

    name = user.get('real_name')
    return '{}, you have been summoned by the all-powerful goob.'.format(name)


if __name__ == "__main__":
    print on_message({'text': '!summon ' + sys.argv[1]}, None)
