"""!haiku [x]: fetch haiku #x|random"""

import re
import random
from limbo import conf
import logging
from redis.client import StrictRedis

REDIS = StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)
QUEUE = "HAIKU"

LOG = logging.getLogger(__name__)

TARGET = [5, 7, 5]
STRINGS = []
COUNTS = []


# Stolen from http://shallowsky.com/blog/programming/count-syllables-in-python.html
def count_syllables(word, verbose=False):
    vowels = ['a', 'e', 'i', 'o', 'u']

    on_vowel = False
    in_diphthong = False
    minsyl = 0
    maxsyl = 0
    lastchar = None

    word = word.lower()
    for c in word:
        is_vowel = c in vowels

        if on_vowel is None:
            on_vowel = is_vowel

        # y is a special case
        if c == 'y':
            is_vowel = not on_vowel

        if is_vowel:
            if verbose:
                print c, "is a vowel"
            if not on_vowel:
                # We weren't on a vowel before.
                # Seeing a new vowel bumps the syllable count.
                if verbose:
                    print "new syllable"
                minsyl += 1
                maxsyl += 1
            elif on_vowel and not in_diphthong and c != lastchar:
                # We were already in a vowel.
                # Don't increment anything except the max count,
                # and only do that once per diphthong.
                if verbose:
                    print c, "is a diphthong"
                in_diphthong = True
                maxsyl += 1
        elif verbose:
            print "[consonant]"

        on_vowel = is_vowel
        lastchar = c

    # Some special cases:
    if word[-1] == 'e':
        minsyl -= 1
    # if it ended with a consonant followed by y, count that as a syllable.
    if word[-1] == 'y' and not on_vowel:
        maxsyl += 1

    return minsyl, maxsyl


def haiku(body):
    """(Accidental) haiku detector"""
    body = body.lower()

    if body.startswith("!"):
        return False

    STRINGS.append(body)
    if len(STRINGS) > 3:
        STRINGS.pop(0)

    syllables = count_syllables(body)
    COUNTS.append(syllables)
    if len(COUNTS) > 3:
        COUNTS.pop(0)
    if len(COUNTS) == 3:
        counts = ", ".join(map(str, COUNTS))
        strings = " / ".join(STRINGS)
        LOG.debug("Checking for haiku: %s\n%s\n" % (counts, strings))
        for i in range(3):
            if not (COUNTS[i][0] <= TARGET[i] <= COUNTS[i][1]):
                break
        else:
            index = REDIS.rpush(QUEUE, strings)
            return "Haiku #%s detected!\n%s\n%s\n" % (index - 1, counts, strings)
    return False


def haikyou(body):
    body = body.lower()

    match = re.match(r"!haiku(\s+(\d+))?", body)
    if not match:
        return False

    index = match.group(2)
    if index is None:
        index = random.randrange(0, REDIS.llen(QUEUE))
    return REDIS.lindex(QUEUE, index)


def on_message(msg, server):
    text = msg.get("text", "")
    return haiku(text) or haikyou(text)
