"""
!translate (<from:lang code> optional original lang) (<to:lang code> optional translated language, en default) <phrase>. Codes: https://cloud.google.com/translate/v2/using_rest#language-params
"""
from textblob import TextBlob
import re
import sys

def detect_language(phrase):
    blob = TextBlob(phrase)
    return blob.detect_language()

def get_languages_string(match):
    phrase = match.group('phrase')
    from_lang = match.group('from_lang')
    to_lang = match.group('to_lang')

    if to_lang is None:
        to_lang = 'en'
    if from_lang is None:
        from_lang = detect_language(phrase)

    return phrase, from_lang, to_lang

def translate(phrase, from_lang, to_lang='en'):
    blob = TextBlob(phrase)

    try:
        translation = blob.translate(from_lang=from_lang, to=to_lang)
        return translation.string
    except:
        return "Sorry, no translation!"

def on_message(msg, server):
    text = msg.get("text", "")

    match = re.search(r"!translate( from\:(?P<from_lang>\S+))?( to:(?P<to_lang>\S+))? (?P<phrase>.+)", text)

    if not match:
        return

    phrase, from_lang, to_lang = get_languages_string(match)

    return translate(phrase, from_lang, to_lang)

if __name__ == '__main__':
    print on_message({'text': '!translate from:es to:de Hola' + \
            ' '.join(sys.argv[1:])}, None)
