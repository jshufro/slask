"""!dolan returns a random dolan comic from the google image search result for <search term>"""

import re
from image import image

def on_message(msg, server):
    text = "dolan comic"
    match = re.findall(r"!image (.*)", text)
    if not match:
        return

    searchterm = match[0]
    return image(searchterm.encode("utf8"))