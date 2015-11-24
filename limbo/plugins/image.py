"""!image <search term> return a random result from the google image search result for <search term>"""

try:
    from urllib import quote, unquote
except ImportError:
    from urllib.request import quote, unquote
import re
import requests
from random import shuffle
import logging
from limbo import LAST_MESSAGE

LOG = logging.getLogger(__name__)


def image(searchterm, unsafe=False):
    searchterm = quote(searchterm)

    safe = "&safe=" if unsafe else "&safe=active"
    searchurl = "https://www.google.com/search?tbm=isch&q={0}{1}".format(searchterm, safe)

    # this is an old iphone user agent. Seems to make google return good results.
    useragent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"

    result = requests.get(searchurl, headers={"User-agent": useragent}).text

    images = re.findall(r'imgurl.*?(http.*?)\\', result)
    shuffle(images)

    if images:
        image = images[0]
        try:
            return unquote(image[:image.index('&amp;imgrefurl')])
        except ValueError:
            LOG.warn(image, exc_info=True)
            return unquote(image)
    else:
        return ""

def on_message(msg, server):
    text = msg.get("text", "")

    if text == "!dolan":
        return image("dolan comic")

    searchterm = None

    match = re.findall(r"!image (.*)", text)
    if match:
        searchterm = LAST_MESSAGE + match[0]
    match = re.findall(r"!plus (.*)")
    if match:
        searchterm = match[0]
    if searchterm:
        return image(searchterm.encode("utf8"))
    return False
