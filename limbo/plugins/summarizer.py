import redis
import json
import requests
import time

from limbo import conf

R = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)

PREFIX = 'optbot:history:'  # redis key namespace for opt-bot history

def get_username(user_id):
    token = 'xoxp-2543006699-3669524994-6723996225-a82588'
    users_url = 'https://slack.com/api/users.info?token={}&user={}'.format(token, user_id)
    r = requests.get(users_url)
    return r.json().get('user').get('name')

# key-value functions

def on_message(msg, server):
    text = msg.get("text", "")
    if text == "!history":
        resp = ""
        for k in sorted(R.keys(PREFIX + '*')):
            for m in R.lrange(k, 0, -1):
                val = json.loads(m)
                t = time.strftime("%a, %d %b %Y %H:%M:%S",
                                  time.localtime(int(float(val['ts']))))
                resp += str(t) + val['user'] + ": " + val['text'] + "\n"
        return resp

    v = dict()
    v['text'] = text
    v['user'] = get_username(msg.get("user", ""))
    v['ts'] = msg.get("ts", "")
    ts = int(float(v['ts']))

    key = PREFIX + str(ts)
    val = json.dumps(v)

    R.rpush(key, val)
    R.expire(key, 24 * 60 * 60)
    return


