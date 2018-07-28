# tag::enumimport[]
import enum
# end::enumimport[]
# tag::namedtuple[]
from collections import namedtuple
# end::namedtuple[]
__all__ = [
    'Player',
    'Point',
]


# tag::color[]
class Player(enum.Enum):
    black = 1
    white = 2

    def __str__(self):
        return str(-1 * (self.value * 2 - 3))
    
    def __int__(self):
        return -1 * (self.value * 2 - 3)
        
    @property
    def other(self):
        return Player.black if self == Player.white else Player.white
# end::color[]


# tag::points[]
class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]
# end::points[]

    def __deepcopy__(self, memodict={}):
        # These are very immutable.
        return self
