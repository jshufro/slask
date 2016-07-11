"""
!cw new [width, height] - new crossword game
!cw submit 1 a word - submit an answer
!cw ghost 1 a word - ghost an answer
!cw across - get all across clues
!cw down - get all down clues
!cw all - get all clues
!cw clue 1 a - get a single clue
!cw display - display board
!cw clear 1 a - clear a clue
!cw permalink - get a link to image
"""

import re
import urllib2
from datetime import datetime
from cPickle import dump, load
import logging
import shutil
import socket

from imgurpython import ImgurClient

from puzcw import Puzzle, BoardDimensionException

PUZZLE = Puzzle()
CLIENT_ID = '480dd133b9e74f1'
CLIENT_SECRET = '5e69d9f7e87ef10fc2d5ddf3b9fc882135516e3a'
IMGUR_CLIENT = ImgurClient(CLIENT_ID, CLIENT_SECRET)
MOTHERLOAD = 'http://www.jacobshufro.com/xwords2/puzs/'
CACHED_PUZZLE = '/var/goob/saved_cw'
APACHE_FILE = '/var/www/html/cw.png'
PERMALINK = socket.gethostname() + '.adnexus.net/cw.png'


INVALID_MSG = "Invalid cw functionality, boi"
PARAM_MSG = "What a blunder. Is your command right?"

logger = logging.getLogger('limbo.limbo')

def format_clues(clues):
    clues = map(lambda x: '%s. %s' % (x.num, x.clue), clues)
    return '\n'.join(clues)

def save_to_apache_server():
    path = PUZZLE.save_game()
    shutil.copyfile(path, APACHE_FILE)
    return path

def display(params):
    path = save_to_apache_server()
    resp = IMGUR_CLIENT.upload_from_path(path)
    return resp.get('link', 'Hm, no link, try %s' % path)

def new(params):
    global PUZZLE

    logger.info("In new function")
    day = datetime.now()
    attempts = 0
    while attempts < 10:
        try:
            url = MOTHERLOAD + day.strftime('%y.%m.%d.puz')
            logger.info("Crossword URL %s" % url)
            PUZZLE = Puzzle.from_url(url)
            return display(params)
        except urllib2.HTTPError:
            attempts += 1
            day = day - timedelta(days=1)
    return None

def clue(params):
    num, direction = params
    return PUZZLE.get_clue(num, direction).clue

def across(params):
    resp = "```ACROSS\n%s```"
    clues = format_clues(PUZZLE.across_clues)
    return resp % clues

def down(params):
    resp = "```DOWN\n%s```"
    clues = format_clues(PUZZLE.down_clues)
    return resp % clues

def all_clues(params):
    return across(params) + '\n\n' + down(params)

def submit(params):
    num, direction, word = params
    PUZZLE.submit(num, direction, word)
    save_to_apache_server()
    return 'Submitted!' #display(params)

def ghost(params):
    num, direction, word = params
    PUZZLE.ghost(num, direction, word)
    save_to_apache_server()
    return 'Ghosted!' #display(params)

def clear(params):
    num, direction = params
    PUZZLE.clear(num, direction)
    save_to_apache_server()
    return 'Cleared!' #display(params)

def permalink(params):
    return PERMALINK

def save_to_file():
    # Copy to apache server
    # Cache puzzle to file
    f = open(CACHED_PUZZLE, 'w')
    dump(PUZZLE, f)
    f.close()

def load_from_file():
    try:
        f = open(CACHED_PUZZLE, 'r')
        res = load(f)
        f.close()
        logger.info("Loaded cached puzzle!")
        return res
    except IOError:
        return None

def evaluate_command(cmd):
    # Match command
    cmd_map = {
        'new': new,
        'clue': clue,
        'across': across,
        'down': down,
        'all': all_clues,
        'submit': submit,
        'ghost': ghost,
        'display': display,
        'clear': clear,
        'permalink': permalink
    }
    s = cmd.split(' ')
    cmd_name = s[0]
    params = s[1:]
    fn = cmd_map.get(cmd_name, None)
    if fn is None:
        return INVALID_MSG
    else:
        try:
            return fn(params)
        # Likely a param error!
        except ValueError as e:
            return PARAM_MSG

def on_message(msg, server):
    global PUZZLE

    # Determine if match
    text = msg.get("text", "")
    match = re.findall(r"!(?:cw) (.*)", text)
    if not match:
        return

    # Load puzzle from file
    if not PUZZLE.board:
        PUZZLE = load_from_file()

    # Evaluate command
    res = evaluate_command(match[0])

    #Save puzzle to file
    save_to_file()

    # Return response
    return res
