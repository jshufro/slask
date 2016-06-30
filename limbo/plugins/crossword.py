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
"""

import re
from imgurpython import ImgurClient

from cw.crossword import Crossword
from cw.crossword_exception import BoardDimensionException

PUZZLE = Crossword()
CLIENT_ID = '480dd133b9e74f1'
CLIENT_SECRET = '5e69d9f7e87ef10fc2d5ddf3b9fc882135516e3a'
IMGUR_CLIENT = ImgurClient(CLIENT_ID, CLIENT_SECRET)

INVALID_MSG = "Invalid cw functionality, boi"
PARAM_MSG = "What a blunder. Is your command right?"

def format_clues(clues):
    clues = map(lambda x: '%s. %s' % (x.num, x.clue), clues)
    return '\n'.join(clues)

def display(params):
    path = PUZZLE.save_game()
    resp = IMGUR_CLIENT.upload_from_path(path)
    return resp.get('link', 'Hm, no link, try %s' % path)

def new(params):
    try:
        PUZZLE.init_game(*params)
        return display(params)
    except BoardDimensionException as e:
        return 'Non square board detected, please pass n and m'

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
    return 'Submitted!' #display(params)

def ghost(params):
    num, direction, word = params
    PUZZLE.ghost(num, direction, word)
    return 'Ghosted!' #display(params)

def clear(params):
    num, direction = params
    PUZZLE.clear(num, direction)
    return 'Cleared!' #display(params)

def crossword(cmd):
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
        'clear': clear
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
    text = msg.get("text", "")
    print "In the crossword!!"
    match = re.findall(r"!(?:cw) (.*)", text)
    if not match:
        return
    return crossword(match[0])
