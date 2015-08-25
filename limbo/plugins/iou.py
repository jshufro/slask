import re
import logging
import conf
import json
from redis.client import StrictRedis


LOG = logging.getLogger(__name__)
REDIS = StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
KEY = "goob_IOU"
MAKE_IT_RAIN = "http://uproxx.files.wordpress.com/2013/10/blogging-blogger-computer-raining-money.gif"
BEER_ME = "http://cl.jroo.me/z3/U/r/B/d/a.aaa-Everybody-loves-beer.jpg"
PREFIX = "optimization@conference.appnexus.com"


def on_message(msg, server):
    """!iou [cashout]: Show|cash out IOUs"""
    body = msg.get("text", "").lower()

    match = re.match(r"thanks?\s+(you\s+)?gooby?(\s*\+(\d+))?",
                     body,
                     flags=re.IGNORECASE)
    if match:
        response = json.loads(server.slack.api_call("users.info", user=msg["user"]))
        from_ = response["user"]["profile"]["real_name"]
        if from_.startswith(PREFIX):
            from_ = from_[len(PREFIX) + 1:]
        REDIS.hincrby(KEY, from_, amount=int(match.group(3) or 1))

    cashout = False
    if not match:
        match = re.match(r"!iou(\s+(\w+))?", body)
        if match:
            cashout = match.group(2) == "cashout"

    if not match:
        return False

    all_ = []
    for key, value in REDIS.hgetall(KEY).items():
        all_.append("%-20s : %5s" % (key, value))

    if cashout:
        REDIS.delete(KEY)
        all_.append("CHA-CHING!!\n%s" % MAKE_IT_RAIN)

    if not all_:
        all_.append("Beer me bruh?\n%s" % BEER_ME)

    return "\n".join(all_)
