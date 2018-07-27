import copy
import pickle
import numpy as np

import zobrist_2 as zobrist
from gotypes import Player, Point
from scoring import compute_game_result

__all__ = [
    'Board',
    'GameState',
    'Move',
]

STONE_TO_CHAR = {
    None: ' . ',
    Player.black: ' x ',
    Player.white: ' o ',
}

neighbor_tables = {}
corner_tables = {}


def init_neighbor_table(dim):
    rows, cols = dim
    new_table = {}
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            p = Point(row=r, col=c)
            full_neighbors = p.neighbors()
            true_neighbors = [
                n for n in full_neighbors
                if 1 <= n.row <= rows and 1 <= n.col <= cols]
            new_table[p] = true_neighbors
    neighbor_tables[dim] = new_table


def init_corner_table(dim):
    rows, cols = dim
    new_table = {}
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            p = Point(row=r, col=c)
            full_corners = [
                Point(row=p.row - 1, col=p.col - 1),
                Point(row=p.row - 1, col=p.col + 1),
                Point(row=p.row + 1, col=p.col - 1),
                Point(row=p.row + 1, col=p.col + 1),
            ]
            true_corners = [
                n for n in full_corners
                if 1 <= n.row <= rows and 1 <= n.col <= cols]
            new_table[p] = true_corners
    corner_tables[dim] = new_table


class IllegalMoveError(Exception):
    pass


class GoString():
    """Stones that are linked by a chain of connected stones of the
    same color.
    """

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return GoString(self.color, self.stones, new_liberties)

    def merged_with(self, string):
        """Return a new string containing all stones in both strings."""
        assert string.color == self.color
        combined_stones = self.stones | string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | string.liberties) - combined_stones)

    @property
    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties

    def __deepcopy__(self, memodict={}):
        return GoString(self.color, self.stones, pickle.loads(pickle.dumps(self.liberties)))
        # return GoString(self.color, self.stones, copy.deepcopy(self.liberties))


class Board():
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        assert num_cols == num_rows
        self.board_size = self.num_cols
        self.action_space = self.set_action_space()
        self._grid = {}
        self._hash = zobrist.EMPTY_BOARD

        global neighbor_tables
        dim = (num_rows, num_cols)
        if dim not in neighbor_tables:
            init_neighbor_table(dim)
        if dim not in corner_tables:
            init_corner_table(dim)
        self.neighbor_table = neighbor_tables[dim]
        self.corner_table = corner_tables[dim]

    def set_action_space(self):
        rv = [0 for y in range(self.board_size)
              for x in range(self.board_size)]
        rv.append(0)  # for pass
        rv.append(0)  # for resign 
        return np.array(rv)

    def neighbors(self, point):
        return self.neighbor_table[point]

    def corners(self, point):
        return self.corner_table[point]

    def place_stone(self, player, point):
        assert self.is_on_grid(point)
        if self._grid.get(point) is not None:
            print('Illegal play on %s' % str(point))
        assert self._grid.get(point) is None
        # 0. Examine the adjacent points.
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []
        for neighbor in self.neighbor_table[point]:
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)
# tag::apply_zobrist[]
        # 1. Merge any adjacent strings of the same color.
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string
        # Remove empty-point hash code.
        self._hash ^= zobrist.HASH_CODE[point, None]
        # Add filled point hash code.
        self._hash ^= zobrist.HASH_CODE[point, player]
# end::apply_zobrist[]

        # 2. Reduce liberties of any adjacent strings of the opposite
        #    color.
        # 3. If any opposite color strings now have zero liberties,
        #    remove them.
        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)

    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        for point in string.stones:
            # Removing a string can create liberties for other strings.
            for neighbor in self.neighbor_table[point]:
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            self._grid[point] = None
            # Remove filled point hash code.
            self._hash ^= zobrist.HASH_CODE[point, string.color]
            # Add empty point hash code.
            self._hash ^= zobrist.HASH_CODE[point, None]

    def is_self_capture(self, player, point):
        friendly_strings = []
        for neighbor in self.neighbor_table[point]:
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                # This point has a liberty. Can't be self capture.
                return False
            elif neighbor_string.color == player:
                # Gather for later analysis.
                friendly_strings.append(neighbor_string)
            else:
                if neighbor_string.num_liberties == 1:
                    # This move is real capture, not a self capture.
                    return False
        if all(neighbor.num_liberties == 1 for neighbor in friendly_strings):
            return True
        return False

    def will_capture(self, player, point):
        for neighbor in self.neighbor_table[point]:
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                continue
            elif neighbor_string.color == player:
                continue
            else:
                if neighbor_string.num_liberties == 1:
                    # This move would capture.
                    return True
        return False

    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    def get(self, point):
        """Return the content of a point on the board.

        Returns None if the point is empty, or a Player if there is a
        stone on that point.
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        """Return the entire string of stones at a point.

        Returns None if the point is empty, or a GoString if there is
        a stone on that point.
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def __eq__(self, other):
        return isinstance(other, Board) and \
            self.num_rows == other.num_rows and \
            self.num_cols == other.num_cols and \
            self._hash() == other._hash()

    def __deepcopy__(self, memodict={}):
        copied = Board(self.num_rows, self.num_cols)
        # Can do a shallow copy b/c the dictionary maps tuples
        # (immutable) to GoStrings (also immutable)
        copied._grid = copy.copy(self._grid)
        copied._hash = self._hash
        return copied

# tag::return_zobrist[]
    def zobrist_hash(self):
        return self._hash
# end::return_zobrist[]


class Move():
    """Any action a player can play on a turn.

    Exactly one of is_play, is_pass, is_resign will be set.
    """

    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        """A move that places a stone on the board."""
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)

    def __str__(self):
        if self.is_pass:
            return 'pass'
        if self.is_resign:
            return 'resign'
        return '(r %d, c %d)' % (self.point.row, self.point.col)


class GameState():
    def __init__(self, board, playerTurn, previous, move):
        self.board = board
        self.board_size = board.board_size
        self.PASS_INDEX = self.board_size ** 2
        self.RESIGN_INDEX = self.board_size ** 2 + 1
        self.playerTurn = playerTurn
        self.previous_state = previous
        if previous is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.playerTurn, previous.board.zobrist_hash())})
        self.last_move = move
        self.allowedActions = self.legal_indices()
        self.id = self._convertStateToId()
        self.newState = None
        self.pieces = {1: 'X', 0: '-', -1: 'O'}
        self.value = self._getValue()
        self.score = self._getScore()

    def _getValue(self):
        # This is the value of the state for the current player
        # i.e. if the previous player played a winning move, you lose
        score = 0
        if self.is_over():
            score = int(self.winner())
            if score == -1 * int(self.playerTurn):
                return (-1, -1, 1)
            else:
                return (-1, 1, -1)
        return (0, 0, 0)

    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2])

    def _convertStateToId(self):
        lines = []
        for row in range(self.board.num_rows, 0, -1):
            line = []
            for col in range(1, self.board.num_cols + 1):
                stone = self.board.get(Point(row=row, col=col)) or '0'
                line.append(str(stone))
            lines.append(''.join(line))
        _id = ''.join(lines)

        str_actions = '-'.join(map(str, self.allowedActions))
        _id += '-' + str_actions
        if self.previous_state and self.previous_state.last_move and self.previous_state.last_move.is_pass:
            _id += '1'
        else:
            _id += '0'
        if self.last_move and self.last_move.is_pass:
            _id += '1'
        else:
            _id += '0'
        if self.last_move and self.last_move.is_resign:
            _id += '1'
        else:
            _id += '0'
        return _id

    def dump_state_example(self):
        lines = []
        for row in range(self.board.num_rows, 0, -1):
            line = []
            for col in range(1, self.board.num_cols + 1):
                stone = self.board.get(Point(row=row, col=col)) or 0
                if stone:
                    stone = stone.value * 2 - 3
                line.append(stone)
            lines.append(line)
        return np.array(lines).reshape(1, self.board_size, self.board_size)

    def apply_move(self, move):
        """Return the new GameState after applying the move."""
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.playerTurn, move.point)
        else:
            next_board = self.board
        self.newState = GameState(next_board, self.playerTurn.other, self, move)
        return self.newState

    def index_to_loc(self, index):
        x = index // self.board_size + 1
        y = index % self.board_size + 1
        return x, y

    def takeAction(self, index):
        done = 0
        value = 0
        if self.is_over():
            return self, int(self.winner()), 1
        # TODO Add done check here !1
        if index == self.PASS_INDEX:
            move = Move.pass_turn()
        elif index == self.RESIGN_INDEX:
            move = Move.resign()
        else:
            x, y = self.index_to_loc(index)
            point = Point(row=x, col=y)
            move = Move.play(point)
        # raise NotImplementedError('fix values below')
        newState = self.apply_move(move)
        if newState.is_over():
            done = 1
            value = newState.winner() or 0
        return newState, int(value), done

    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_move_self_capture(self, player, move):
        if not move.is_play:
            return False
        return self.board.is_self_capture(player, move.point)

    @property
    def situation(self):
        return (self.playerTurn, self.board)

    def does_move_violate_ko(self, player, move):
        if not move.is_play:
            return False
        if not self.board.will_capture(player, move.point):
            return False
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (
            self.board.get(move.point) is None and
            not self.is_move_self_capture(self.playerTurn, move) and
            not self.does_move_violate_ko(self.playerTurn, move))

    def is_over(self):
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def legal_moves(self):
        if self.is_over():
            return []
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        # These two moves are always legal.
        moves.append(Move.pass_turn())
        moves.append(Move.resign())

        return moves
    
    def legal_indices(self):
        moves = self.legal_moves()
        indices = [(x.point.row - 1) * self.board_size + x.point.col - 1 for x in moves if x.point]
        indices.append(self.PASS_INDEX)
        indices.append(self.RESIGN_INDEX)
        return np.array(indices)

    def winner(self):
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.playerTurn
        game_result = compute_game_result(self)
        return int(game_result.winner)

    def render(self, logger):
        lines = []
        for row in range(self.board.num_rows, 0, -1):
            line = []
            for col in range(1, self.board.num_cols + 1):
                stone = self.board.get(Point(row=row, col=col))
                line.append(STONE_TO_CHAR[stone])
            lines.append(''.join(line))
        board = '\n'.join(lines)
        logger.info(board)
        logger.info('--------------')
