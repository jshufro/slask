"""!image <search term> return a random result from the google image search result for <search term>"""

try:
    from urllib import quote
except ImportError:
    from urllib.request import quote
import re
import requests
from random import shuffle
import logging

LOG = logging.getLogger(__name__)
LAST_MESSAGE = ""
USERAGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36"

def octal_to_html_escape(re_match):
    # an octal escape of the form '\75' (which ought to become '%3d', the
    # url-escaped form of "=". Strip the leading \
    s = re_match.group(0)[1:]

    # convert octal to hex and strip the leading '0x'
    h = hex(int(s, 8))[2:]

    return "%{0}".format(h)

def unescape(url):
    # google uses octal escapes for god knows what reason
    return re.sub(r"\\..", octal_to_html_escape, url)

def image(searchterm, unsafe=False, isgif=False):
    searchterm = quote(searchterm)

    safe = "" if unsafe else "&safe=active"
    gif = "&tbs=itp:animated" if isgif else ""
    searchurl = "https://www.google.com/search?tbm=isch&q={0}{1}{2}".format(searchterm, safe, gif)

    result = requests.get(searchurl, headers={"User-agent": USERAGENT}).text

    images = re.findall(r"\"ou\":\"(.*?)\",", result)
    # images = list(map(unescape, re.findall(r"\"ou\":\"(.*?)\",", result)))
    shuffle(images)

    return images[0] if images else ""

def on_message(msg, server):
    text = msg.get("text", "")

    if text == "!dolan":
        return image("dolan comic")

    searchterm = None
    isgif = False

    # image
    match = re.findall(r"!image (.*)", text)
    if match:
        searchterm = LAST_MESSAGE + match[0]

    # plus image
    match = re.findall(r"!plus (.*)", text)
    if match:
        searchterm = match[0]

    # gif
    match = re.findall(r"!gif (.*)", text)
    if match:
        searchterm = match[0]
        isgif = True

    # search
    if searchterm:
        return image(searchterm.encode("utf8"), isgif=isgif)

    return False
