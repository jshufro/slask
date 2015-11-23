"""!genesis returns a random sega genesis screenshot"""

import re
import requests
import hashlib
from random import choice
from limbo.conf import flickr_client_key, flickr_client_secret

def sign(params):
    md5 = hashlib.md5()
    md5.update(flickr_client_secret)
    for key in sorted(params):
        md5.update(key)
        md5.update(str(params[key]))
    return md5.hexdigest()


def genesis():
    api_endpoint = "https://api.flickr.com/services/rest"

    params = {
        "method": "flickr.photosets.getPhotos",
        "api_key": flickr_client_key,
        "photoset_id": 72157646180733361,
        "format": "json",
        "nojsoncallback": 1
    }
    params["api_sig"] = sign(params)
    r = requests.get(api_endpoint,
                     params=params,
                     verify=False)
    photo = choice(r.json()["photoset"]["photo"])

    params = {
        "method": "flickr.photos.getSizes",
        "api_key": flickr_client_key,
        "photo_id": photo["id"],
        "format": "json",
        "nojsoncallback": 1
    }
    params["api_sig"] = sign(params)
    r = requests.get(api_endpoint,
                     params=params,
                     verify=False)

    for size in r.json()["sizes"]["size"]:
        if size["label"] == "Medium":
            return photo["title"] + "\n" + size["source"]

def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!genesis", text)
    if not match:
        return
    return genesis()


if __name__ == "__main__":
    print genesis()
