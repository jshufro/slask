"""!urbandictionary something"""
import re
try:
    from urllib import quote, unquote
except ImportError:
    from urllib.request import quote, unquote

URBANDICTIONARY = "http://www.urbandictionary.com/define.php?term="

def urbandictionary(q):
    query = q.replace(' ', '+')
    return URBANDICTIONARY + (query)


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!urbandictionary (.*)", text)
    if not match:
        return

    return urbandictionary(match[0])

