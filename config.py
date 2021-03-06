#### SELF PLAY
# EPISODES = 5
# MCTS_SIMS = 50
# MEMORY_SIZE = 30000

EPISODES = 5 
# EPISODES = 75 
MCTS_SIMS = 10
# MCTS_SIMS = 50
MEMORY_SIZE = 2000 

# TURNS_UNTIL_TAU0 = 20  # turn on which it starts playing deterministically
TURNS_UNTIL_TAU0 = 8  # turn on which it starts playing deterministically
CPUCT = 1
EPSILON = 0.2
ALPHA = 0.8


#### RETRAINING
BATCH_SIZE = 256
EPOCHS = 1
REG_CONST = 0.0001
LEARNING_RATE = 0.1
MOMENTUM = 0.9
TRAINING_LOOPS = 10

HIDDEN_CNN_LAYERS = [
    {'filters': 75, 'kernel_size': (2, 2)},
    {'filters': 75, 'kernel_size': (2, 2)},
    {'filters': 75, 'kernel_size': (2, 2)},
    {'filters': 75, 'kernel_size': (2, 2)},
    {'filters': 75, 'kernel_size': (2, 2)},
    {'filters': 75, 'kernel_size': (2, 2)}
]

#### EVALUATION
EVAL_EPISODES = 20
SCORING_THRESHOLD = 1.3
