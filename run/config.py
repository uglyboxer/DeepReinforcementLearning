#### SELF PLAY
EPISODES = 30 
MCTS_SIMS = 10
MEMORY_SIZE = 30000

# EPISODES = 10
# MCTS_SIMS = 5 
# MEMORY_SIZE = 100

TURNS_UNTIL_TAU0 = 10  # turn on which it starts playing deterministically
CPUCT = 1
EPSILON = 0.2
ALPHA = 0.8


#### RETRAINING
BATCH_SIZE = 256
EPOCHS = 30
REG_CONST = 0.0001
LEARNING_RATE = 0.1
MOMENTUM = 0.9
TRAINING_LOOPS = 50

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
