"""$<ticker symbol> for a quote on a stock price"""
from __future__ import print_function
import logging
import re
try:
    from urllib import quote
except ImportError:
    from urllib.request import quote

from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

def stockprice(ticker):
    url = "https://www.google.com/finance?q={0}"
    soup = BeautifulSoup(requests.get(url.format(quote(ticker))).text, "html5lib")


    try:
        title = re.match(r'(.*?)quotes', soup.title.string).group(1)
    except IndexError:
        logging.info("Unable to find stock {0}".format(ticker))
        return ""
    try:
        price = soup.select("#price-panel .pr span")[0].text
        change, pct = soup.select("#price-panel .nwp span")[0].text.split()
        pct.strip('()')
        price_info = "{} {} {}".format(price, change, pct)
    except IndexError:
        price_info = soup.select("#price-panel")[0].text.strip()

    emoji = ":chart_with_upwards_trend:" if ("+") in price_info else ":chart_with_downwards_trend:"

    return "{} {}: {} {}".format(emoji, title, price_info, emoji)


def on_message(msg, server):
    text = msg.get("text", "")
    matches = re.findall(r"\$\w+", text)
    if not matches:
        return

    prices = [stockprice(ticker[1:].encode("utf8")) for ticker in matches]
    return "\n".join(p for p in prices if p)
