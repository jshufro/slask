"""
Replace every noun in a text with the seventh noun after it in a dictionary.
http://en.wikipedia.org/wiki/Oulipo
"""

import nltk
import random
from nltk.stem.wordnet import WordNetLemmatizer
from collections import OrderedDict
import pattern.en
import re


class Cache():
    entries = []
    index = 0
    with open('/usr/share/dict/words', 'r') as f:
        for word in f:
            entries.append((word.rstrip('\n'), index))
            index += 1
    words = OrderedDict(entries)

prev_msg = ""

def n_plus_transform(body):
    """!n+7: perform an n+7 (or any other integer) transformation on text"""
    reg = re.compile('!n\+(\d+)\s*(.*)', re.IGNORECASE)
    match = reg.match(body)

    global prev_msg
    if not match:
        #Maintain last seen message.
        prev_msg = body
        return False

    word_offset = int(match.group(1))
    text = match.group(2) or None

    if not text:
        text = prev_msg

    pos_tags = nltk.pos_tag(nltk.word_tokenize(text))
    lemmatizer = WordNetLemmatizer()

    do_not_prepend_with_space = re.compile("^[,.;:?'].*$")

    out = ""

    for pos_tag in pos_tags:
        word = pos_tag[0]
        #If a noun...
        if pos_tag[1].startswith("N"):
            #Before looking up the noun, get rid of inflection.
            word = lemmatizer.lemmatize(word)
            idx = Cache.words.get(word)
            #If noun is not found in the dictionary...
            if idx is None:
                #...try lowercase
                idx = Cache.words.get(word.lower())
                if idx is None:
                    #...try capitalizing
                    idx = Cache.words.get(word.capitalize())
                    if idx is None:
                        #...find a random replacement.
                        idx = random.randint(0, len(Cache.words)-1)
            idx += word_offset
            if idx >= len(Cache.words):
                idx %= len(Cache.words)
            word = Cache.words.keys()[idx]
            #Try to retain number
            if pos_tag[1] == "NNS" or pos_tag[1] == "NNPS":
                word = pattern.en.pluralize(word)
            #Retain capitalization
            if pos_tag[0][0].isupper():
                word = word.capitalize()
        #Build the new message.
        #No space if (1) first word, (2) preceded by hashtag,
        #or (3) punctuation.
        if not out \
                or out.endswith("#") \
                or do_not_prepend_with_space.match(word):
            out += word
        else:
            out += " " + word

    return out

def on_message(msg, server):
    text = msg.get("text", "")
    return n_plus_transform(text)

