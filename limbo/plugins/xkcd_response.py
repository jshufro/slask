"""!xkcd (#|today|random)? 'link'?: returns an xkcd comic. default random"""

import xkcd
import re

EXPLAIN = "http://www.explainxkcd.com/wiki/index.php/"

def xkcd_response(text):
    match = re.match(r'!xkcd ?(\w+)? ?(\w+)?', text)
    if not match:
        return False

    option = match.group(1)
    link = match.group(2)
    comic = xkcd.getRandomComic()
    if option:
        if option == 'today':
            comic = xkcd.getLatestComic()
        elif option.isdigit():
            comic = xkcd.getComic(int(option))
    if link == 'link':
        return comic.link + '\n' + (EXPLAIN + str(comic.number))
    else:
        return comic.title + '\n' + comic.imageLink + '\n' + comic.altText + '\n' + (EXPLAIN + str(comic.number))

def on_message(msg, server):
    text = msg.get("text", "")
    return xkcd_response(text)
