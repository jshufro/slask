"""!zooborn <search term>: returns a zooborn comic sometimes appropriate for <search term>"""

from bs4 import BeautifulSoup
import requests
from random import randint, shuffle
import sys
import re

def on_message(msg, server):
    body = msg.get('text', '').lower()
    match = re.match(r'!zooborn\s(.*)', body, re.IGNORECASE)
    if not match:
        return False

    description = match.group(1)

    page = randint(1,15)
    url = 'http://www.zooborns.com/zooborns/page/{}/'.format(page)

    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    img_links = soup.find_all('a', class_='asset-img-link')
    shuffle(img_links)
    for img_link in img_links:
        try:
            return "`{0}`: {1}".format(description, img_link.find('img')['src'])
        except:
            print "lule hackathon"

if __name__ == "__main__":
    print on_message({'text': '!zooborn ' + ' '.join(sys.argv[1:])}, None)
