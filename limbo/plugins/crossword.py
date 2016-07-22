"""
!cw new [width, height] - new crossword game
!cw submit 1 a word - submit an answer
!cw ghost 1 a word - ghost an answer
!cw across [remaining] - get all across clues
!cw down [remaining] - get all down clues
!cw all [remaining] - get all clues
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

from puzcw import Crossword

PUZZLE = Crossword()
CLIENT_ID = '480dd133b9e74f1'
CLIENT_SECRET = '5e69d9f7e87ef10fc2d5ddf3b9fc882135516e3a'
IMGUR_CLIENT = ImgurClient(CLIENT_ID, CLIENT_SECRET)
MOTHERLOAD = 'http://www.jacobshufro.com/xwords2/puzs/'
CACHED_PUZZLE = '/var/goob/saved_cw'
APACHE_FILE = '/var/www/html/cw.png'
PERMALINK = socket.gethostname() + '.adnexus.net/cw.png'
CLUE_FMT = "{num}{dir}: {clue}"
INDENT = ">>>"
CLUES_HEADER = "*{title}*\n{clues}"

PARAM_MSG = "What a blunder. Is your command right?"

logger = logging.getLogger('limbo.limbo')

def format_clue(clue):
    res = CLUE_FMT.format(
            num=clue.num,
            dir=clue.clue_type.upper(),
            clue=clue.clue.encode('utf8')
        )
    if clue.submitted:
        return "~"+res+"~"
    else:
        return res

def format_clues(clues, only_remaining=False):
    if only_remaining:
        clues = filter(lambda x: not x.submitted, clues)
    clues = map(format_clue, clues)
    return '\n'.join(clues)

def only_remaining(params):
    if params and params[0]=='remaining':
        return True
    return False

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
            PUZZLE = Crossword.from_url(url)
            return display(params)
        except urllib2.HTTPError:
            attempts += 1
            day = day - timedelta(days=1)
    return None

def clue(params):
    num, direction = params
    clue = PUZZLE.get_clue(num, direction)
    return format_clue(clue)

def across(params):
    clues = format_clues(PUZZLE.across_clues, only_remaining(params))
    return INDENT + CLUES_HEADER.format(title='ACROSS',
                                        clues=clues)

def down(params):
    clues = format_clues(PUZZLE.down_clues, only_remaining(params))
    return INDENT + CLUES_HEADER.format(title='DOWN',
                                        clues=clues)

def all_clues(params):
    across_clues = format_clues(PUZZLE.across_clues, only_remaining(params))
    down_clues = format_clues(PUZZLE.down_clues, only_remaining(params))
    return INDENT \
            + CLUES_HEADER.format(title='ACROSS',
                                  clues=across_clues) \
            + '\n\n' \
            + CLUES_HEADER.format(title='DOWN',
                                  clues=down_clues) \

def submit(params):
    num, direction, word = params
    PUZZLE.submit(num, direction, word)
    save_to_apache_server()
    return 'Submitted %s %s!' % (num, direction) #display(params)

def ghost(params):
    num, direction, word = params
    PUZZLE.ghost(num, direction, word)
    save_to_apache_server()
    return 'Ghosted %s %s!' % (num, direction) #display(params)

def clear(params):
    num, direction = params
    PUZZLE.clear(num, direction)
    save_to_apache_server()
    return 'Cleared %s %s!' % (num, direction) #display(params)

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

def _remove_leading_whitespace(string):
    white = re.match(r"\s*", string)
    return string[white.end():]

def evaluate_command(string):
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

    string = _remove_leading_whitespace(string)
    cmd_regex = r"new|display|permalink|all|across|down|clue|submit|ghost|clear"
    cmd_name = re.match(cmd_regex, string)

    fn = None
    if cmd_name:
        string = string[cmd_name.end():]
        fn = cmd_map[cmd_name.group()]
        cmd_name = cmd_name.group()

    if cmd_name in ["new", "display", "permalink"]:
        string = _remove_leading_whitespace(string)
        if string:
            return PARAM_MSG

        try:
            return fn(string)
        except ValueError as e:
            return PARAM_MSG

    if cmd_name in ["across", "down", "all"]:
        string = _remove_leading_whitespace(string)
        show_remaining = re.match(r"remaining", string)
        if show_remaining:
            string = string[show_remaining.end():]
            show_remaining = show_remaining.group()

        string = _remove_leading_whitespace(string)
        if string:
            return PARAM_MSG

        try:
            return fn(show_remaining)
        except ValueError as e:
            return PARAM_MSG

    string = _remove_leading_whitespace(string)
    clue_number_regex = r"\d+"
    clue_number = re.match(clue_number_regex, string)
    if clue_number:
        string = string[clue_number.end():]
        clue_number = clue_number.group()
    else:
        return PARAM_MSG

    string = _remove_leading_whitespace(string)
    direction_regex = r"[adAD]"
    direction = re.match(direction_regex, string)
    if direction:
        string = string[direction.end():]
        direction = direction.group()
    else:
        return PARAM_MSG

    if cmd_name in ["clue", "clear"]:
        string = _remove_leading_whitespace(string)
        if string:
            return PARAM_MSG

        try:
            return fn([clue_number, direction])
        except ValueError as e:
            return PARAM_MSG

    string = _remove_leading_whitespace(string)
    answer_regex = r"\w+"
    answer = re.match(answer_regex, string)
    if answer:
        string = string[answer.end():]
        answer = answer.group()
    if cmd_name in ["submit", "ghost"]:
        string = _remove_leading_whitespace(string)
        if string:
            return PARAM_MSG

        try:
            return fn([clue_number, direction, answer])
        except ValueError as e:
            raise e
            return PARAM_MSG

    # should have nothing left now
    string = _remove_leading_whitespace(string)
    if string:
        return PARAM_MSG

    # if cmd_name not found, assume "submit" or "clue"
    try:
        if answer:
            return submit([clue_number, direction, answer])
        else:
            return clue([clue_number, direction])
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
