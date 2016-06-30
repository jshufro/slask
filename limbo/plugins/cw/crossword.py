import urllib2
from datetime import datetime, timedelta
import math
from crossword_image import CrosswordImage
from crossword_exception import BoardDimensionException, \
    WriteException

from box import Box
from clues import Clue, Clues, ACROSS_ID, DOWN_ID


MOTHERLOAD = 'http://www.jacobshufro.com/xwords2/puzs/'
NULL = '\x00'
OPEN_BOX = '-'
BLANK = '.'
BOARD_START_KEY = OPEN_BOX*3
BOARD_IDX_KEY = 'NY Times'


class Crossword(object):

    def __init__(self, n=None, m=None):
        self.n = int(n) if n is not None else n
        self.m = int(m) if m is not None else n
        self.board = []
        self.clues = Clues()

    def init_game(self, n=None, m=None):
        """ Retrieve and parse game. """
        self.__init__(n, m)
        game_str = self._download_game()
        self._process_game_str(game_str)
        self.save_game()

    def save_game(self):
        """ Save crossword as image, return path. """
        image = CrosswordImage(self.n, self.m, self.board)
        image.construct_image()
        return image.save()

    def get_clue(self, num, clue_type):
        """ Retrieve clue by key. """
        num = int(num)
        clue_type = clue_type.lower()
        try:
            return self.clues.get_clue(num, clue_type)
        except KeyError:
            return "Clue %s:%s doesn't exist!" % (num, clue_type)

    @property
    def across_clues(self):
        """ Retrieve all across clues. """
        return self.clues.clues_by_type(ACROSS_ID)

    @property
    def down_clues(self):
        """ Retrieve all down clues. """
        return self.clues.clues_by_type(DOWN_ID)

    @property
    def all_clues(self):
        return self.across_clues + self.down_clues

    def _write(self, num, clue_type, word, guess_type):
        clue = self.get_clue(num, clue_type)
        x, y = clue.start_position
        for letter in word:
            box = self.board[x][y]

            # Raise WriteException for blank box
            if box.is_blank: raise WriteException

            box.write(guess_type, clue_type, letter.upper())

            # Increment x or y
            if clue_type == ACROSS_ID:
                y += 1
            else:
                x += 1

    def submit(self, num, clue_type, word):
        self._write(num, clue_type, word, 'submission')

    def ghost(self, num, clue_type, word):
        self._write(num, clue_type, word, 'ghost')

    def clear(self, num, clue_type):
        """ Clear answers from boxes by direction. """
        clue = self.get_clue(num, clue_type)
        x, y = clue.start_position
        while True:
            try:
                box = self.board[x][y]
                if box.is_blank: raise WriteException
                box.clear(clue_type)
                if clue_type == ACROSS_ID:
                    y += 1
                else:
                    x += 1

            # Break at a blank or index error
            except (WriteException, IndexError) as e:
                break

    def _download_game(self):
        """ Download and format game. """
        day = datetime.now()
        attempts = 0
        while attempts < 10:
            try:
                day_str = day.strftime('%y.%m.%d.puz')
                # day_str = '16.07.03.puz'
                url = MOTHERLOAD + day_str
                res = urllib2.urlopen(url)
                ucontent = unicode(res.read(), "ISO-8859-1")
                return ucontent.encode('utf-8')
            except urllib2.HTTPError:
                attempts += 1
                day = day - timedelta(days=1)

    def _process_game_str(self, game_str):
        """ 
        Parse game string and set up game from string.

        The string comes through in the following:
        1. A series of characters with null values separating key items
        2. The board with answers, board with blanks, and date come
            through the same index
        3. Every non-empty element after the board is a clue listed in
            numerical order
        """
        game_list = game_str.split(NULL)

        # Get board
        for idx, data in enumerate(game_list):
            if BOARD_IDX_KEY in data:
                board_idx = idx
                board_str = data
                break

        # Process board string
        self._build_board(board_str, board_idx, game_list)

    def _build_board(self, board_str, board_idx, game_list):
        """ 
        Process the board string the board string. 

        1. Determine index of board start
        2. Determine n
        3. Create board and boxes
        """
        board_start = board_str.index(BOARD_START_KEY)
        sqrt = math.sqrt(board_start)
        is_square = sqrt - int(sqrt) == 0
        if is_square:
            self.n = int(math.sqrt(board_start))
            self.m = self.n
        elif self.n is None or self.m is None:
            msg = "Non square board detected."
            raise BoardDimensionException(msg)

        answer_idx = 0
        clue_count = 1
        clue_idx = board_idx + 3
        for row in range(self.m):
            new_row = []
            for col in range(self.n):

                # Determine info for box and clues
                board_space = board_str[board_start + answer_idx]
                is_blank = board_space==BLANK 
                answer = None if is_blank else board_str[answer_idx]
                is_across = not is_blank and (col==0 or new_row[col-1].is_blank)
                is_down = not is_blank and (row==0 or self.board[row-1][col].is_blank)
                if is_across or is_down:
                    number = clue_count
                    if is_across:
                        clue = Clue(clue=game_list[clue_idx],
                                    start_position=(row,col),
                                    num=number,
                                    clue_type=ACROSS_ID)
                        self.clues.put(clue_count, ACROSS_ID, clue)
                        clue_idx += 1
                    if is_down:
                        clue = Clue(clue=game_list[clue_idx],
                                    start_position=(row,col),
                                    num=number,
                                    clue_type=DOWN_ID)
                        self.clues.put(clue_count, DOWN_ID, clue)
                        clue_idx += 1
                    clue_count += 1
                else:
                    number = None

                # Create and append box
                box = Box(answer=answer,
                          is_blank=is_blank,
                          number=number)
                new_row.append(box)
                answer_idx += 1

            self.board.append(new_row)

