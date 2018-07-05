from game import Game
from funcs import playMatchesBetweenVersions
import loggers as lg

env = Game()
playMatchesBetweenVersions(
env
, 1  # the run version number where the computer player is located
, 6 # the version number of the first player (-1 for human)
, -1 # the version number of the second player (-1 for human)
, 1 # how many games to play
, lg.logger_tourney # where to log the game to
, 1  # which player to go first - 0 for random
)
