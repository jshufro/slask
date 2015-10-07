"""!iou [cashout]: Show|ca$h out goob IOUs"""

import re
import logging
import conf
import json
import random
from redis.client import StrictRedis


LOG = logging.getLogger(__name__)
REDIS = StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
KEY = "goob_IOU"
MAKE_IT_RAIN = [
    "http://uproxx.files.wordpress.com/2013/10/blogging-blogger-computer-raining-money.gif",
    "http://i.imgur.com/lnK1nBF.gif",
    "http://i.imgur.com/ptqA6dW.gif",
    "http://i.imgur.com/r1o0uyH.gif",
    "http://i.imgur.com/N0aYJTJ.gif",
    "http://i.imgur.com/j25gaOc.gif",
    "http://i.imgur.com/tkbHsDZ.gif",
    "http://i.imgur.com/HaNu5ka.gif",
    "http://i.imgur.com/5ZcUxTg.gif",
    "http://i.imgur.com/5CiZA5v.gif",
    "http://i.imgur.com/nDUasjq.gif",
    "http://i.imgur.com/8ExBVb4.gif",
    "http://i.imgur.com/cskbcM2.gif",
    "http://i.imgur.com/49tP7pc.gif",
    "http://i.imgur.com/28bfK1I.gif",
    "http://i.imgur.com/ERyoPf3.gif",
    "http://i.imgur.com/PbADlZW.gif",
    "http://i.imgur.com/dgBtPpD.gif",
    "http://i.imgur.com/2BgTeUI.gif",
    "http://i.imgur.com/OYAgYcf.gif",
    "http://i.imgur.com/gh7uW50.gif",
    "http://i.imgur.com/6fYah3Z.gif",
    "http://i.imgur.com/yuB67q5.gif",
    "http://i.imgur.com/JeEHZL9.gif",
    "http://i.imgur.com/BxFlFvv.gif",
    "http://i.imgur.com/n6K78PG.gif",
    "http://i.imgur.com/AbHWKoc.gif"
]
BEER_ME = "http://cl.jroo.me/z3/U/r/B/d/a.aaa-Everybody-loves-beer.jpg"
PREFIX = "optimization@conference.appnexus.com"


def on_message(msg, server):
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
        all_.append("CHA-CHING!!\n%s" % random.choice(MAKE_IT_RAIN))

    if not all_:
        all_.append("Beer me bruh?\n%s" % BEER_ME)

    return "\n".join(all_)
