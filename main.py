from game.Poker import *
from game.Player import *

if __name__ == '__main__':
    # random.seed(1)
    players = [
        EquityPlayer(1, 10000, 0.5, 0.3),
        EquityPlayer(2, 10000, 0.5, 0.3),
        EquityPlayer(3, 10000, 0.7, 0.5),
        EquityPlayer(4, 10000, 0.7, 0.5),
        RandomPlayer(5),
        RandomPlayer(6)
    ]
    # for i in range(100):
    game = Poker(players, 10, 1000, True, True)
    game.play_game(100)

