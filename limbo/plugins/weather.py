# -*- coding: utf-8 -*-
"""!weather <zip or place name> return the 5-day forecast"""

try:
    from urllib import quote
except ImportError:
    from urllib.request import quote
import os
import re
import requests
import time
import logging
from limbo.conf import goog_api_key, openweather_appid

LOG = logging.getLogger(__name__)

DEFAULT = {
    "lat": 40.741869,
    "lng": -73.990950
}

# http://openweathermap.org/weather-conditions
iconmap = {
    "01": ":sunny:",
    "02": ":partly_sunny:",
    "03": ":partly_sunny:",
    "04": ":cloud:",
    "09": ":droplet:",
    "10": ":droplet:",
    "11": ":zap:",
    "13": ":snowflake:",
    "50": ":umbrella:",    # mist?
}

def weather(searchterm):
    LOG.info("searchterm={0}".format(searchterm))
    location = None
    if not searchterm:
        location = DEFAULT
    else:
        searchterm = quote(searchterm)
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}"
            response = requests.get(url.format(searchterm, goog_api_key))
            try:
                location = response.json()["results"][0]["geometry"]["location"]
            except:
                LOG.warn("Invalid geocoding API response: {0}".format(response.text),
                         exc_info=1)
        except:
            LOG.warn("Could not geocode location", exc_info=1)

    if location:
        method = "lat={0}&lon={1}".format(location["lat"], location["lng"])
    else:
        method = "q={0}".format(searchterm)

    url = 'http://api.openweathermap.org/data/2.5/forecast/daily?{0}&cnt=5&mode=json&units=imperial&APPID={1}'
    url = url.format(method, openweather_appid)

    dat = requests.get(url)
    try:
        dat = dat.json()
    except:
        LOG.warn(dat.text, exc_info=1)

    msg = ["{0}: ".format(dat["city"]["name"])]
    for day in dat["list"]:
        name = time.strftime("%a", time.gmtime(day["dt"]))
        high = str(int(round(float(day["temp"]["max"]))))
        icon = iconmap.get(day["weather"][0]["icon"][:2], ":question:")
        msg.append(u"{0} {1}° {2}".format(name, high, icon))

    return " ".join(msg)

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!weather(.*)", text)
    if not match:
        return

    searchterm = match[0]
    return weather(searchterm.encode("utf8"))
