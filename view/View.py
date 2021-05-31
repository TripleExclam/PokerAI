import tkinter as tk
from tkinter import messagebox
from game.PlayerList import PlayerList
from game.Action import Action
from treys import Card, Evaluator, Deck
import time


class Player(tk.Frame):
    def __init__(self, master, name):
        super().__init__(master)
        self.name = tk.Label(master, text=name)
        self.name.pack()

        self.stack = tk.Label(master, text="")
        self.stack.pack()

        self.hand = tk.Label(master, text="")
        self.hand.pack()

    def set_stack(self, stack):
        self.stack.config(text=stack)

    def set_hand(self, hand):
        self.hand.config(text=hand)

class Application:
    def __init__(self, root):
        self.root = root
        self.players = []
        for i in range(6):
            player = Player(self.root, f"Player {i+1}")
            player.pack()
            self.players.append(player)

        self.running = True
        self.update_event = None
        self.cards = tk.Label(self.root, text="")
        self.cards.pack(side=tk.BOTTOM)

    def pause(self):
        self.after_cancel(self.update_event)
        self.running = False

    def resume(self, game):
        self.running = True
        self.update_event = self.root.after(100, self.update, game)

    def update(self, game):
        if len(game.players) <= 1:
            self.handle_close(game)
            return

        self.play_game(game)
        self.update_event = self.root.after(100, lambda: self.update(game))

    def handle_close(self, game):
        messagebox.showinfo('End of game', 'End of game')
        self.root.destroy()

    def handle_keypress(self, event, game):
        if event.char == " ":
            if self.running:
                self.pause()
            else:
                self.resume(game)

    def play_game(self, game):
        self.play_round(game)
        game.board = []
        game.rotate_button()
        stack_sum = 0
        for player in game.players[:]:
            stack_sum += player.stack
            if player.stack < game.big_blind:
                game.players.remove(player)
            print(player.uuid, player.stack)
            self.players[player.uuid - 1].set_stack(player.stack)
        assert stack_sum == 6000, "Failed stack sum :("

    def play_round(self, game):
        pot = 0
        game.all_in = False
        game.player_list = PlayerList(game.players)
        game.reset_bets()
        self.deal_cards(game)

        game.history = {player.uuid: [] for player in game.players}
        # Charge the blinds
        game.step_blind(False)  # Small blind
        game.step_blind(True)  # Big Blind

        avail_actions = [Action.FOLD, Action.CALL] + game.BET_ACTIONS  # First round allows players to respond to blinds
        for k in [3, 1, 1]:  # Flop, Turn and River cards
            if game.all_in:  # No more betting to take place
                self.comm_cards(game, k)
                continue
            pot += game.betting_round(avail_actions)
            avail_actions = [Action.FOLD, Action.CHECK] + game.BET_ACTIONS
            game.reset_bets()

            if len(game.player_list) == 1:
                break

            self.comm_cards(game, k)  # Reveal cards after each betting round

        winner = game.calculate_winner()
        winner.add_stack(pot)

        print(winner.uuid, "wins with" + Card.print_pretty_cards(winner.cards))

    def deal_cards(self, game):
        """
        Reset the deck and deal cards for a new hand
        """
        game.deck.shuffle()
        for player in game.players:
            player.set_cards(game.deck.draw(2))  # Texas Hold'em gives each player 2 cards.

            self.players[player.uuid - 1].set_hand(Card.print_pretty_cards(player.cards))
            print(player.uuid, Card.print_pretty_cards(player.cards))

    def comm_cards(self, game, n):
        if n > 1:
            game.board += game.deck.draw(n)
        else:
            game.board.append(game.deck.draw(1))

        self.cards.config(text=Card.print_pretty_cards(game.board))
        print(Card.print_pretty_cards(game.board))


    def play(self, game):
        self.root.bind('<KeyPress>', lambda e: self.handle_keypress(e, game))
        self.resume(game)
        self.root.mainloop()
