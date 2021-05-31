import tkinter as tk
from view import View
from PIL import Image, ImageTk
from game.Poker import *
from game.Player import *

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0, 0)
    root.title("Poker")
    root.geometry("612x437")

    app = View.Application(root=root)

    players = [
        EquityPlayer(1, 10000, 0.5, 0.3),
        EquityPlayer(2, 10000, 0.5, 0.3),
        EquityPlayer(3, 10000, 0.7, 0.5),
        EquityPlayer(4, 10000, 0.7, 0.5),
        RandomPlayer(5),
        RandomPlayer(6)
    ]

    game = Poker(players, 10, 1000, True)
    app.play(game)


