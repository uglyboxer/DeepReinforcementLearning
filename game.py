import numpy as np
import logging
import pickle

from go_board import Board


class Game:

    def __init__(self):     
        self.currentPlayer = 1
        self.board_size = 4
        self.gameState = Board(board_size=self.board_size, playerTurn=-1)
        self.actionSpace = self.gameState.action_space
        self.pieces = {'1':'X', '0': '-', '-1':'O'}
        self.grid_shape = (self.gameState.board_size, self.gameState.board_size)
        self.input_shape = (2, self.grid_shape[0], self.grid_shape[1])
        self.name = 'Go'
        self.state_size = 2 #len(self.gameState.binary)
        self.action_size = len(self.actionSpace)

    def reset(self):
        self.gameState = Board(self.board_size, playerTurn=1)
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

        currentBoard = state.history
        currentAV = actionValues

        state_copy = state.newState 
        # currentBoard = np.array([
        #       currentBoard[6], currentBoard[5],currentBoard[4], currentBoard[3], currentBoard[2], currentBoard[1], currentBoard[0]
        #     , currentBoard[13], currentBoard[12],currentBoard[11], currentBoard[10], currentBoard[9], currentBoard[8], currentBoard[7]
        #     , currentBoard[20], currentBoard[19],currentBoard[18], currentBoard[17], currentBoard[16], currentBoard[15], currentBoard[14]
        #     , currentBoard[27], currentBoard[26],currentBoard[25], currentBoard[24], currentBoard[23], currentBoard[22], currentBoard[21]
        #     , currentBoard[34], currentBoard[33],currentBoard[32], currentBoard[31], currentBoard[30], currentBoard[29], currentBoard[28]
        #     , currentBoard[41], currentBoard[40],currentBoard[39], currentBoard[38], currentBoard[37], currentBoard[36], currentBoard[35]
        #     ])

        # currentAV = np.array([
        #     currentAV[6], currentAV[5],currentAV[4], currentAV[3], currentAV[2], currentAV[1], currentAV[0]
        #     , currentAV[13], currentAV[12],currentAV[11], currentAV[10], currentAV[9], currentAV[8], currentAV[7]
        #     , currentAV[20], currentAV[19],currentAV[18], currentAV[17], currentAV[16], currentAV[15], currentAV[14]
        #     , currentAV[27], currentAV[26],currentAV[25], currentAV[24], currentAV[23], currentAV[22], currentAV[21]
        #     , currentAV[34], currentAV[33],currentAV[32], currentAV[31], currentAV[30], currentAV[29], currentAV[28]
        #     , currentAV[41], currentAV[40],currentAV[39], currentAV[38], currentAV[37], currentAV[36], currentAV[35]
        #             ])

        # identities.append((Board(state.board_size, currentBoard, state.playerTurn), currentAV))
        identities.append((state_copy, currentAV))

        return identities
        