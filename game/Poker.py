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
        self.bet_count = self.MAX_RAISES
        self.player_list = PlayerList(self.players)
        self.history = {}
        self.bets = {}

    def reset_bets(self):
        self.bets = {player.uuid: 0 for player in self.players}

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

    def calculate_winner(self):
        """
        Determin the winner of a hand using smart encodings supplied by treys
        :param players: Remaining players in the game
        """
        if len(self.player_list) <= 1:  # Only check for winners if necessary
            return self.player_list.rotation[0]

        evaluator = Evaluator()
        best = (None, float('inf'))

        for player in self.player_list.rotation:
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

    def step_blind(self, is_big):
        player = self.player_list.next_player()

        action = Action.BET1BB
        amount = self.big_blind / (1 if is_big else 2)
        self.history[player.uuid].append((action, amount))
        self.bets[player.uuid] += amount
        self.player_list.visited = 1  # Blinds can bet again on top of their stake
        player.add_stack(-amount)

        return action, amount

    def step_bets(self, avail_actions):
        ind = self.player_list.pos
        player = self.player_list.next_player()

        action = player.act(self.get_game_state(ind, self.history), avail_actions)
        amount = self.get_amount(player, action)
        if amount >= player.stack:
            action = Action.CALL if self.all_in else Action.ALLIN

        self.history[player.uuid].append((action, amount))
        if action == Action.FOLD:
            self.player_list.remove(player)  # player is not participating in this hand
            return avail_actions

        # If a player raises or calls, we calculate the remainder they need to pay.
        debt = max(self.bets.values()) - self.bets[player.uuid]
        amount = min(amount + debt, player.stack)  # Effectively places the player all-in if they cannot afford
        player.add_stack(-amount)

        self.bets[player.uuid] += amount

        if action != Action.CALL and action != Action.CHECK:
            self.bet_count -= 1
            self.player_list.visited = 1  # Re-visit all proceeding players
            avail_actions = [Action.FOLD, Action.CALL]
            self.all_in = action == Action.ALLIN  # TODO: support re-raising an all-in

            if not self.all_in and self.bet_count > 0:
                avail_actions += self.BET_ACTIONS

        return avail_actions

    def betting_round(self, avail_actions) -> int:
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
        self.bet_count = self.MAX_RAISES

        while not self.player_list.visited_all():
            avail_actions = self.step_bets(avail_actions)

        if self.display:
            print("ACTIONS:", self.history)
            print("BETS", self.bets)

        self.player_list.visited = 0  # Reset for the next hand
        return sum(self.bets.values())

    def play_round(self):
        """
        Executes a hand of poker
        """
        pot = 0
        self.all_in = False
        self.player_list = PlayerList(self.players)
        self.reset_bets()
        self.deal_cards()

        self.history = {player.uuid: [] for player in self.players}
        # Charge the blinds
        self.step_blind(False)  # Small blind
        self.step_blind(True)  # Big Blind

        avail_actions = [Action.FOLD, Action.CALL] + self.BET_ACTIONS  # First round allows players to respond to blinds
        for k in [3, 1, 1]:  # Flop, Turn and River cards
            if self.all_in:  # No more betting to take place
                self.comm_cards(k)
                continue
            pot += self.betting_round(avail_actions)
            avail_actions = [Action.FOLD, Action.CHECK] + self.BET_ACTIONS
            self.reset_bets()

            if len(self.player_list) == 1:
                break

            self.comm_cards(k)  # Reveal cards after each betting round

        winner = self.calculate_winner()
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
            stack_sum = 0
            for player in self.players[:]:
                stack_sum += player.stack
                if player.stack < self.big_blind:
                    self.players.remove(player)
                print(player.uuid, player.stack)
            assert stack_sum == 6000, "Failed stack sum :("
            n -= 1
