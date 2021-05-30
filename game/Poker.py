from treys import Card, Evaluator, Deck
from game.PlayerList import PlayerList
from game.Action import Action

class Poker:
    MAX_RAISES = 3  # Maximum number of times a player can raise / bet in a round
    BET_ACTIONS = [Action.BET1BB, Action.BET3BB, Action.BET4BB, Action.BET5BB, Action.ALLIN]

    def __init__(self, participants, big_blind, starting_stack, display=False):
        """
        No Limit Texas Hold'em Engine powered by 'treys'

        :param big_blind: Cost of playing a hand
        :param starting_stack: Number of chips each player begins with
        :param display: Whether or not to show the actions taken in the game
        :param participants: List of players in the game
        """
        self.display = display
        self.big_blind = big_blind
        self.players = [x for x in participants]
        for player in participants:
            player.add_stack(starting_stack - player.stack)

        self.deck = Deck()
        self.board = []
        self.all_in = False

    def rotate_button(self):
        """
        Move the responsibility of posting the big-blind
        """
        self.players = self.players[1:] + [self.players[0]]

    def deal_cards(self):
        """
        Reset the deck and deal cards for a new hand
        """
        self.deck.shuffle()
        for player in self.players:
            player.set_cards(self.deck.draw(2))  # Texas Hold'em gives each player 2 cards.

            if self.display:
                print(player.uuid, Card.print_pretty_cards(player.cards))

    def comm_cards(self, n):
        """
        Deals cards into the board

        :param n: Number of cards to deal
        """
        if n > 1:
            self.board += self.deck.draw(n)
        else:
            self.board.append(self.deck.draw(1))

        if self.display:
            print(Card.print_pretty_cards(self.board))

    def calculate_winner(self, players):
        """
        Determin the winner of a hand using smart encodings supplied by treys
        :param players: Remaining players in the game
        """
        if len(players) <= 1:  # Only check for winners if necessary
            return players.rotation[0]

        evaluator = Evaluator()
        best = (None, float('inf'))

        for player in players.rotation:
            card_eval = evaluator.evaluate(self.board, player.cards)
            if self.display:
                print(Card.print_pretty_cards(player.cards),
                      evaluator.class_to_string(evaluator.get_rank_class(card_eval)))
            if card_eval < best[1]:
                best = (player, card_eval)

        return best[0]

    def get_game_state(self, player, history):
        """
        Summarises the game in a dictionary. Needs work...
        :param player: Index of current player
        :param history: All actions in the given hand
        :return: All available information in the game
        """
        assert player < len(self.players)
        return {
            "board": self.board,
            "history": history,
            "position": player
        }

    def get_amount(self, player, action):
        """
        The amount of chips a player bids given an action
        :param player: Current player
        :param action: Action.py
        :return: Amount of chips
        """
        return min(player.stack, action.bet_mul * self.big_blind)  # Players bet scaled by their stack

    def betting_round(self, players, bets, history, avail_actions) -> int:
        """
        Handle a single round of betting
        If a bet is placed, give all players a chance to respond
        Once all players have either folded or checked / called yields the pot

        :param bets: Betting history
        :param history: Hand history
        :param avail_actions: Actions available at the start of the round
        :param players: PlayerList of those participating in the hand
        :return: The total amount staked
        """
        bet_count = self.MAX_RAISES

        while not players.visited_all():
            ind = players.pos
            player = players.next_player()

            action = player.act(self.get_game_state(ind, history), avail_actions)
            amount = self.get_amount(player, action)
            if amount >= player.stack:
                action = Action.CALL if self.all_in else Action.ALLIN

            history[player.uuid].append((action, amount))
            if action == Action.FOLD:
                players.remove(player)  # player is not participating in this hand
                continue

            # If a player raises or calls, we calculate the remainder they need to pay.
            debt = max(bets.values()) - bets[player.uuid]
            amount = min(amount + debt, player.stack)  # Effectively places the player all-in if they cannot afford
            player.add_stack(-amount)

            bets[player.uuid] += amount

            if action != Action.CALL and action != Action.CHECK:
                bet_count -= 1
                players.visited = 1  # Re-visit all proceeding players
                avail_actions = [Action.FOLD, Action.CALL]
                self.all_in = action == Action.ALLIN  # TODO: support re-raising an all-in

                if not self.all_in and bet_count > 0:
                    avail_actions += self.BET_ACTIONS

        if self.display:
            print("ACTIONS:", history)
            print("BETS", bets)

        players.visited = 0  # Reset for the next hand
        return sum(bets.values())

    def play_round(self):
        """
        Executes a hand of poker
        """
        self.all_in = False
        active_players = PlayerList(self.players)
        pot = 0
        self.deal_cards()

        # Charge the blinds
        active_players.next_player().add_stack(-self.big_blind / 2)
        active_players.next_player().add_stack(-self.big_blind)
        active_players.visited = 0  # Blinds can bet again on top of their stake
        bets = {player.uuid: self.big_blind / (2 - ind) if ind <= 1 else 0
                for ind, player in enumerate(self.players)}
        history = {player.uuid: [(Action.BET1BB, self.big_blind / (2 - ind))] if ind <= 1 else []
                   for ind, player in enumerate(self.players)}
        avail_actions = [Action.FOLD, Action.CALL] + self.BET_ACTIONS  # First round allows players to respond to blinds

        for k in [3, 1, 1]:  # Flop, Turn and River cards
            if self.all_in:  # No more betting to take place
                self.comm_cards(k)
                continue
            pot += self.betting_round(active_players, bets, history, avail_actions)
            avail_actions = [Action.FOLD, Action.CHECK] + self.BET_ACTIONS
            if len(active_players) == 1:
                break

            self.comm_cards(k)  # Reveal cards after each betting round

        winner = self.calculate_winner(active_players)
        winner.add_stack(pot)

        if self.display:
            print(winner.uuid, "wins with" + Card.print_pretty_cards(winner.cards))

    def play_game(self, n):
        """
        Executes a game of poker until a winner emerges or n games are played
        :param n: Number of games to play
        """
        while n > 0 and len(self.players) > 1:
            if self.display:
                print("\n-------------NEW GAME-------------\n")

            self.play_round()
            self.board = []
            self.rotate_button()
            for player in self.players[:]:
                if player.stack < self.big_blind:
                    self.players.remove(player)
                print(player.uuid, player.stack)
            n -= 1
