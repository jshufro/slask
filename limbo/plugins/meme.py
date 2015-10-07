"""!meme <template> <up>/<down>: only denk memes"""

import re
import requests
import json
from collections import namedtuple


API = 'http://memegen.link'
TEMPLATES = None


Template = namedtuple('Template', ['id', 'name', 'url', 'description', 'aliases'])


def _templates():
    global TEMPLATES
    if TEMPLATES is None:
        response = requests.get(API + '/templates').json()
        TEMPLATES = {}
        for meme, endpoint in response.iteritems():
            id = endpoint[endpoint.rindex('/'):]
            info = requests.get(endpoint).json()
            template = Template(id=id,
                                name=meme,
                                url=API + id,
                                description=info['description'],
                                aliases=info['aliases'])
            TEMPLATES[id[1:]] = template
    return TEMPLATES


def _help(templates):
    memes = []
    for meme in templates.itervalues():
        memes.append(meme._asdict())
    return "```%s```" % json.dumps(memes,
                                   indent=4,
                                   sort_keys=True,
                                   separators=(',', ': '))


def on_message(msg, server):
    body = msg.get('text', '').lower()

    reg = re.compile('^!meme(gen)?(.+)?', re.IGNORECASE)
    match = reg.match(body)

    if not match:
        return False

    templates = _templates()

    if not match.group(2):
        return _help(templates)

    parts = str(match.group(2)).lower().split()
    meme, text = parts[0], ' '.join(parts[1:])

    try:
        template = TEMPLATES[meme]
    except KeyError:
        for template in TEMPLATES.itervalues():
            if meme in template.aliases:
                break
        else:
            return _help(templates)

    try:
        up, down = text.split('/')
    except ValueError:
        up, down = text, ''
    response = requests.get('/'.join([template.url, up, down]))
    if not response.ok:
        return "```%s```" % response.json()
    return response.json()['direct']['masked']


if __name__ == '__main__':
    print on_message({'text': '!meme whine almond milk in iced coffee/cheese curds'}, None)
