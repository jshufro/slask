import wolframalpha
import re

APP_ID = "468AA5-HPV64AY622"
client = wolframalpha.Client(APP_ID)


def wolfram_response(text):
    """!what|!why|!which|!who|!where|!when!how: just give you an answer"""
    match = re.match(r"(^!what|!why|!which|!who|!where|!when|!how) (.*)", text)
    if not match:
        return False
    query = match.group(0).replace('!', '')
    return wolfram_it(query)

def ask_response(text):
    """!ask: ask the magic guru a question."""
    match = re.match(r"!ask (.*)", text)
    if not match:
        return False
    query = match.group(1)
    return wolfram_it(query)
ask_response._is_response = True


def wolfram_it(query):
    result = client.query(query)
    response = ''
    interpreted_response = ''
    for i in result.pods:
        if ('Input' in i.title):
            interpreted_response = str(i.text)
        elif i.text:
            response += i.text.replace(u'\xb0F', '')
            break

    if response:
        return response
    elif interpreted_response:
        return interpreted_response


def on_message(msg, server):
    text = msg.get("text", "")
    return wolfram_response(text) or ask_response(text)

