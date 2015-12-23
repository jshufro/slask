"""!amazon <query> will return the top Amazon result for that query"""
from bs4 import BeautifulSoup
import re
try:
    from urllib import quote, unquote, urlopen
except ImportError:
    from urllib.request import quote, unquote

def amazon(q):
    query = quote(q)
    url = "http://www.amazon.com/s?url=search-alias%3Daps&field-keywords={0}".format(query)

    page = urlopen(url)
    soup = BeautifulSoup(page.read(), 'html.parser')

    for link in soup.find_all('a', class_='a-link-normal a-text-normal'):
        if "http://www.amazon.com" not in link['href']:
            continue
        else:
            return link['href']
    return "Did you mean :neverforget:?"

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!amazon (.*)", text)
    if not match:
        return

    return amazon(match[0])
