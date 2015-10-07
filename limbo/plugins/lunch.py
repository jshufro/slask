"""!lunch|dinner menu: suggest a lunch menu"""

import sys
import json
import random
import requests
import re
from conf import goog_api_key


BOUNDS = "40.741869, -73.990950"


def search(item=None):
    if item is not None:
        meal = item
    else:
        meal = 'lunch'
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    payload = {
        "key": goog_api_key,
        "location": BOUNDS,
        "radius": 100,
        "types": "restaurant",
        "sensor": "false",
        "query": meal
    }
    result = requests.get(url, params=payload)
    return json.loads(result.text)


def on_message(msg, server):
    body = msg.get('text', '').lower()
    reg = re.compile('^!(lunch|dinner)(\s(\w+))?', re.IGNORECASE)
    match = reg.match(body)
    if not match:
        return False
    m = search(item=match.group(3))
    if len(m['results']) == 0:
        return "Found nothing: get what you ate yesterday"
    result = random.choice(m['results'])
    response = 'Restaurant: ' + result['name'] + '\n'
    response += 'Address: ' + result['formatted_address'] + '\n'
    try:
        response += 'Price: ' + ('$' * result['price_level']) + '\n'
    except KeyError:
        pass
    try:
        response += 'Rating: ' + str(result['rating'])
    except KeyError:
        pass
    return response


if __name__ == "__main__":
    print on_message({'text': '!lunch ' + sys.argv[1]}, None)
