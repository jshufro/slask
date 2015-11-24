import redis
import json
from limbo import conf

R = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)

PREFIX = 'optbot:history:'  # redis key namespace for opt-bot history

# key-value functions


def on_message(msg, server):

    text = msg.get("text", "")
    if text == "!history":
        resp = ""
        for k in sorted(R.keys(PREFIX + '*')):
            for m in R.lrange(k, 0, -1):
                val = json.loads(m)
                resp += val['user'] + ": " + val['text'] + "\n"
        return resp

    v = dict()
    v['text'] = text
    v['user'] = msg.get("user", "")
    v['ts'] = msg.get("ts", "")
    ts = int(float(v['ts']))

    key = PREFIX + str(ts)
    val = json.dumps(v)

    R.rpush(key, val)
    R.expire(key, 24 * 60 * 60)
    return


