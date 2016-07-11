from collections import namedtuple


ACROSS_ID = 'a'
DOWN_ID = 'd'


ClueKey = namedtuple('ClueKey', ['num', 'clue_type'])


class Clue(object):

    def __init__(self, clue, start_position, num, clue_type):
        self.clue = clue
        self.start_position = start_position
        self.num = num
        self.clue_type = clue_type

    def __repr__(self):
        return '%s:%s:%s' % (self.clue, self.num, self.clue_type)


class Clues(object):

    def __init__(self):
        self.clues = {}

    def put(self, num, clue_type, clue):
        k = ClueKey(num, clue_type)
        self.clues[k] = clue

    @property
    def sorted_clue_keys(self):
        return sorted(self.clues.keys())

    def clues_by_type(self, clue_type):
        l = filter(lambda x: x.clue_type==clue_type, 
                   self.sorted_clue_keys)
        return [self.clues[x] for x in l]

    def get_clue(self, num, clue_type):
        k = ClueKey(num, clue_type)
        return self.clues[k]