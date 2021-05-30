from game.Poker import *
from game.Player import *

if __name__ == '__main__':
    # random.seed(1)
    players = [
        RandomPlayer(1),
        RandomPlayer(2),
        RandomPlayer(3),
        RandomPlayer(4)
    ]
    # for i in range(100):
    game = Poker(players, 10, 1000, True)
    game.play_game(10)
