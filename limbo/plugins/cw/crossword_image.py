import os
from tempfile import mkstemp
from PIL import Image, ImageDraw, ImageFont

MODE = 'RGB'
WHITE = 'rgb(255,255,255)'
LIGHT_GREY = 'rgb(175,175,175)'
BOX_SIZE = 50
Y_TEXT_OFFSET = -2
NUMBER_OFFSET = 4
ANSWER_OFFSET = 13
FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class CrosswordImage(object):

    def __init__(self, n, m, board):
        self._board = board
        self._width = n*BOX_SIZE
        self._height = m*BOX_SIZE
        self._image = Image.new(MODE, (self._width+1, self._height+1),
                                color=WHITE)
        self._draw = ImageDraw.Draw(self._image)
        self._num_font = None
        self._text_font = None
        self._num_font = ImageFont.truetype(FILE_PATH+"/FreeSans.ttf", 
                                            size=ANSWER_OFFSET)
        self._text_font = ImageFont.truetype(FILE_PATH+"/FreeSans.ttf", 
                                             size=BOX_SIZE-int(1.75*ANSWER_OFFSET))

    def construct_image(self):
        self._create_grid()
        self._populate_grid()

    def _create_grid(self):
        """ Create lines for grid. """
        # Draw row
        for i in range(0, self._height+1, BOX_SIZE):
            self._draw.line(((0,i),(self._width,i)), fill=128)

        # Draw column
        for i in range(0, self._width+1, BOX_SIZE):
            self._draw.line(((i,0),(i,self._height)), fill=128)

    def _populate_grid(self):
        """ Populate grid with items. """
        x, y = 0, 0
        for row in self._board:
            for box in row:
                # Fill in blank boxes
                if box.is_blank:
                    corner1 = (x, y)
                    corner2 = (x+BOX_SIZE, y+BOX_SIZE)
                    self._draw.rectangle((corner1, corner2), fill=128)
                # Fill in empty boxes
                else:
                    # Fill in numbers
                    number = str(box.number) if box.number else ''
                    loc = (x+NUMBER_OFFSET, y+NUMBER_OFFSET+Y_TEXT_OFFSET)
                    self._draw.text(loc, number, fill=128, font=self._num_font)
                    # Fill in text
                    loc = (x+ANSWER_OFFSET, y+ANSWER_OFFSET+Y_TEXT_OFFSET)
                    if box.has_submission:
                        print 'submit: %s' % box.latest_submission
                        self._draw.text(loc, box.latest_submission, fill=128, 
                                        font=self._text_font)
                    elif box.has_ghost:
                        print 'ghost: %s' % box.latest_ghost
                        self._draw.text(loc, box.latest_ghost, fill=LIGHT_GREY,
                                        font=self._text_font)

                # Move to the next boxes
                x = (x + BOX_SIZE) % self._width
            y = y + BOX_SIZE

    def save(self):
        _handle, path = mkstemp()
        path += '.png'
        # self._image.save('testcw.png', 'PNG')
        self._image.save(path, 'PNG')
        return path

