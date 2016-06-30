from time import time
from collections import namedtuple

AnswerTuple = namedtuple('AnswerTuple', 'val ts')

class Box(object):

    def __init__(self, answer, is_blank, number):
        self.answer = answer
        self.is_blank = is_blank
        self.number = number

        # Filled in later
        self._submission = {}
        self._ghost = {}

    def __str__(self):
        number = 0 if self.number is None else self.number
        answer = '_' if self.answer is None else self.answer
        return '%s:%s' % (number, answer)

    def clear(self, clue_type):
        """ Clear box object. """
        self._submission.pop(clue_type, None)
        self._ghost.pop(clue_type, None)

    def write(self, write_type, clue_type, letter):
        """ Write a letter with timestamp. """
        cache = getattr(self, '_%s' % write_type)
        cache[clue_type] = AnswerTuple(val=letter, ts=time())

    @property
    def has_submission(self):
        return len(self._submission) > 0

    @property
    def has_ghost(self):
        return len(self._ghost) > 0

    @property
    def latest_submission(self):
        latest = AnswerTuple(val='', ts=0)
        for k, v in self._submission.iteritems():
            if v.ts > latest.ts:
                latest = v
        return latest.val

    @property
    def latest_ghost(self):
        latest = AnswerTuple(val='', ts=0)
        for k, v in self._ghost.iteritems():
            if v.ts > latest.ts:
                latest = v
        return latest.val