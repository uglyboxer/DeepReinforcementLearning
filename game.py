import numpy as np
import logging
import pickle

from game_2 import Board, GameState


class Game:

    def __init__(self):     
        self.currentPlayer = 1
        self.board_size = 9
        self.board = Board(self.board_size, self.board_size)
        self.gameState = GameState(self.board, self.currentPlayer, None, None) 
        self.actionSpace = self.board.action_space
        self.pieces = {'1':'X', '0': '-', '-1':'O'}
        self.grid_shape = (self.gameState.board_size, self.gameState.board_size)
        self.input_shape = (self.grid_shape[0], self.grid_shape[1])
        self.name = 'Go'
        self.state_size = 2 #len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def reset(self):
        self.gameState = GameState.new_game(self.board_size)
        self.currentPlayer = 1
        return self.gameState

    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)
        self.gameState = next_state
        self.currentPlayer = -self.currentPlayer
        info = None
        return (next_state, value, done, info)

    def identities(self, state, actionValues):
        identities = [(state, actionValues)]

        currentAV = actionValues
        state_copy = state.newState 
        identities.append((state_copy, currentAV))

        return identities
        
