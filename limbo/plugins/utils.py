"""X OR Y: let goob make all your important life decisions
!date: UTC time
!dt: UTC time
!greeting: seasons greetings from goob
!blame : what's your excuse?
!ping: pong
!budget query <X> : link to budget age metrics <for X hours> (defaults to 2)"""

import re
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def choose_one(body):
    reg = re.compile(r'(.*) OR (.*)')
    match = reg.match(body)
    if not match:
        return False
    return random.choice([match.group(1), match.group(2)])

def date_response(body):
    excuses = ["Sorry, I'm taken.",
               "You're nice, but not my type.",
               "I think I'm busy that day.",
               "I only date other chat bots.",
               "I think we should get to know each other first."]
    reg = re.compile('!date', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    return random.choice(excuses)

def greeting_response(body):
    excuses = ["Why, hellooooo there.",
               "Hey, how you doin'? ;)",
               "Top o' the morning to ya, laddie.",
               "How's my favorite person doing today?",
               "Yo yo yo, it's your boy goob.",
               "Good (morning | afternoon | evening).",
               "Fancy seeing you here.",
               "Hey there :).",
               "Mai boii now das wut im tawkin bout.",
               "How's it goin my brother from another mother? (or sister from another mister)",
               "Welcome to my humble abode.",
               "Sup?",
               "Hola amigo.",
               "What do you want?"]
    reg = re.compile('!greeting', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    return random.choice(excuses)

def dt_response(body):
    reg = re.compile('!dt', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") + " UTC"

def blame(body):
    reg = re.compile('!blame', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    response = requests.get('http://developerexcuses.com/')
    if response.status_code != 200:
        return "Error"
    data = response.text
    soup = BeautifulSoup(data)
    reply = soup.findAll('a')[0].text
    return reply

def pong(body):
    reg = re.compile('!ping', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    return "pong. http://www.ponggame.org/"

def budget_query_age(body):
    reg = re.compile(r'!budget query\s?(?P<hours>\d+)?', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    if match.group('hours'):
        lookback = int(match.group('hours'))
    else:
        lookback = 2

    url = """https://metrics.adnxs.net/render?width=1100&from=-{}hours&until=now&height=700&target=*.prod.etl-optimization.lax1.optimization.capacity_metrics.budget.query.daily&target=*.prod.etl-optimization.lax1.optimization.capacity_metrics.budget.query.lifetime"""
    url = url.format(lookback)
    return url


ALL = [choose_one,
       date_response,
       greeting_response,
       dt_response,
       blame,
       pong,
       budget_query_age]


def on_message(msg, server):
    text = msg.get("text", "")
    for fn in ALL:
        response = fn(text)
        if response:
            return response

