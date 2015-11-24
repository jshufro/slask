import redis
import json
import requests
import time
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import logging

from limbo import conf

LOGGER = logging.getLogger(__name__)


class FrequencySummarizer:
  def __init__(self, min_cut=0.1, max_cut=0.9):
    """
     Initilize the text summarizer.
     Words that have a frequency term lower than min_cut
     or higer than max_cut will be ignored.
    """
    self._min_cut = min_cut
    self._max_cut = max_cut
    self._stopwords = set(stopwords.words('english') + list(punctuation))
    LOGGER.info(self._stopwords)

  def _compute_frequencies(self, word_sent):
    """
      Compute the frequency of each of word.
      Input:
       word_sent, a list of sentences already tokenized.
      Output:
       freq, a dictionary where freq[w] is the frequency of w.
    """
    LOGGER.info('in compute frequencies')
    freq = defaultdict(int)
    for s in word_sent:
      for word in s:
        if word not in self._stopwords:
          freq[word] += 1
    # frequencies normalization and filtering
    m = float(max(freq.values()))
    for w in freq.keys():
      freq[w] = freq[w]/m
      if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
        del freq[w]
    return freq

  def summarize(self, sents, n):
    """
      Return a list of n sentences
      which represent the summary of text.
    """
    LOGGER.info('in summarize')

    # sents = sent_tokenize(text)
    LOGGER.info(sents)
    assert n <= len(sents)
    word_sent = [word_tokenize(s.lower()) for s in sents]
    self._freq = self._compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i, sent in enumerate(word_sent):
      for w in sent:
        if w in self._freq:
          ranking[i] += self._freq[w]
    sents_idx = self._rank(ranking, n)
    return [sents[j] for j in sents_idx]

  def _rank(self, ranking, n):
    """ return the first n sentences with highest ranking """
    LOGGER.INFO('in _rank')
    return nlargest(n, ranking, key=ranking.get)


R = redis.StrictRedis(host=conf.redis_host, port=conf.redis_port, db=conf.redis_db)

PREFIX = 'optbot:history:'  # redis key namespace for opt-bot history

def get_username(user_id):
    token = 'xoxp-2543006699-3669524994-6723996225-a82588'
    users_url = 'https://slack.com/api/users.info?token={}&user={}'.format(token, user_id)
    r = requests.get(users_url)
    return r.json().get('user').get('name')

def history():
    resp = ""
    for k in sorted(R.keys(PREFIX + '*')):
        for m in R.lrange(k, 0, -1):
            val = json.loads(m)
            t = time.strftime("%a, %d %b %Y %H:%M:%S",
                              time.localtime(int(float(val['ts']))))
            resp += str(t) + "   " + val['user'] + ": " + val['text'] + "\n"
    return resp

def on_message(msg, server):
    text = msg.get("text", "")
    if text == "!history":
        return history()

    if text == "!summarize":
        fs = FrequencySummarizer()
        sents = []
        for k in sorted(R.keys(PREFIX + '*')):
            for m in R.lrange(k, 0, -1):
                val = json.loads(m)
                sents.append(val['text'])
        return fs.summarize(sents, 10)

    v = dict()
    v['text'] = text
    v['user'] = get_username(msg.get("user", ""))
    v['ts'] = msg.get("ts", "")
    ts = int(float(v['ts']))

    key = PREFIX + str(ts)
    val = json.dumps(v)

    R.rpush(key, val)
    R.expire(key, 24 * 60 * 60)
    return


