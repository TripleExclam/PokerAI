from game.Poker import *
from agents.EquityPlayer import *
from agents.RandomPlayer import *
from game.GameWrapper import *
import json
import matplotlib.pyplot as plt
from matplotlib.table import Table


def run_game():
    players = [
        RandomPlayer(1),
        RandomPlayer(2)
    ]
    # for i in range(100):
    game = Poker(players, 10, 1000, True, True)
    game.play_game(100)


if __name__ == '__main__':
    # run_game()
    wrap = GameWrapper()
    util = wrap.train(10000)

    x = {1: 2, 3: 4}
    y = dict(x)
    y[1] = 3
    print(x)
