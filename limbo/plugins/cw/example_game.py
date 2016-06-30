from cPickle import dumps, loads
from tempfile import mkstemp

from crossword import Crossword

def format_clues(clues):
    clues = map(lambda x: '%s. %s' % (x.num, x.clue), clues)
    return '\n'.join(clues)

if __name__ == "__main__":
    puzzle = Crossword()
    puzzle.init_game(16, 15)
    print puzzle.get_clue(1, 'a').clue
    print puzzle.get_clue(2, 'a')
    print format_clues(puzzle.across_clues)
    print format_clues(puzzle.down_clues)
    print puzzle.all_clues
    puzzle.submit(1, 'a','PAIN')
    puzzle.submit(1, 'd', 'plains')
    puzzle.clear(1, 'a')
    puzzle.ghost(4, 'd', 'clams')
    puzzle.ghost(1, 'a','pear')
    puzzle.clear(1, 'a')
    puzzle.submit(65, 'a', 'Monk')
    puzzle.submit(48, 'd', 'drunks')
    puzzle.clear(65, 'a')
    # puzzle.ghost(1, 'd','PANE')
    print puzzle.save_game()
    # _handle, path = mkstemp()
    # f = open(path, 'w')
    # f.write(dumps(puzzle))
    # f.close()
    # f = open(path, 'r')
    # f.read()


