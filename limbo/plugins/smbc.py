"""!smbc (#|today|random)?: returns an smbc comic. default=random"""

from bs4 import BeautifulSoup
from math import floor
from random import random
from requests import get
import re


BASE_URL = "http://www.smbc-comics.com/"


def smbc_response(text):
    match = re.match(r"!smbc ?(\w+)? ?(\w+)?", text)
    if not match:
        return False
    option = match.group(1)

    url = BASE_URL
    if not option or option == "random":
        num = int(floor(random() * 3497))
        url += "?id=%s" % num
    elif option.isdigit():
        url += option
    url += "#comic"

    try:
        r = get(url)
        return url + "\n" + BeautifulSoup(r.text).find(id="comic").img["src"]
    except:
        return url

def on_message(msg, server):
    text = msg.get("text", "")
    return smbc_response(text)
