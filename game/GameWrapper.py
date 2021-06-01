from Poker import *
from agents.EquityPlayer import *
from agents.RandomPlayer import *
from util.Node import *

class GameWrapper:

    def __init__(self):
        self.game_states = {}
        self.players = [
            RandomPlayer(1),
            RandomPlayer(2)
        ]
        self.game = Poker(self.players, 20, 1000, True)
        self.actions = []
        self.step = 0
        self.reward = 0
        self.to_move = 1

    def hole_card_state(self):
        curr_player = self.game.players[self.to_move]
        # hand_eval = round(EquityPlayer.eval_hand(
        #     curr_player.cards, self.game.board, len(self.game.player_list)), 1)
        # Summarise complex states
        opponent_acts = [','.join(y) for x, y in self.game.history.items() if x != curr_player.uuid]
        return ','.join(opponent_acts) + Card.print_pretty_cards(curr_player.cards)

    def train(self, iterations, ante=1.0, bet1=2.0, bet2=8.0, print_interval=1000000):
        ''' Do ficticious self-play to find optimal strategy'''
        util = 0.0

        for i in range(iterations):
            if i % print_interval == 0 and i != 0:
                print("\rP1 expected value after %i iterations: %f" % (i, util / i))

            # Start a game
            actions = self.start_game()
            history = list()
            util += self.cfr(actions, history, 1, 1)

        return util / iterations

    def get_strategy(self):
        """
        Gives the action played by each player based on the game states
        """
        return -1

    def cfr(self, actions, history, p1, p2):
        player = self.game.player_list.next_player()

        probability_weight = p1 if self.game.player_list.pos == 1 else p2

        # Check if state is terminal
        if self.game.player_list.visited_all():
            # Direct payout
            return self.evaluation()

        # Current game state
        state = self.hole_card_state()
        if state in self.game_states:
            node = self.game_states[state]  # Get our node if it already exists
            actions = node.actions_
        else:
            # Create new Node with possible actions we can perform
            node = Node(actions)
            self.game_states[state] = node

        strategy = node.get_strategy(probability_weight)
        util = dict()
        node_util = 0
        # for each of our possible actions, compute the utility of it
        # thus, finding the overall utility of this current state
        for action in actions:
            next_history = list(history)  # copy the game state
            next_history.append(action)

            if self.game.player_list.pos == 1:
                util[action] = -self.cfr(
                    cards, next_history, p1 * strategy[action], p2)
            else:
                util[action] = -self.cfr(
                    cards, next_history, p1, p2 * strategy[action])

            node_util += strategy[action] * util[action]

        # compute regret and update Game State for the node based on utility of all actions
        for action in actions:
            regret = util[action] - node_util
            if player == 0:
                node.regret_sum_[action] += regret * p2
            else:
                node.regret_sum_[action] += regret * p1

        return node_util

    def start_game(self):
        game = self.game
        self.step = 0

        game.all_in = False
        game.player_list = PlayerList(game.players)
        game.reset_bets()
        game.deal_cards()

        game.history = {player.uuid: [] for player in game.players}
        game.step_blind(False)  # Small blind
        game.step_blind(True)  # Big Blind

        return [Action.FOLD, Action.CALL] + game.BET_ACTIONS  # First round allows players to respond to blinds

    def step_bets(self, avail_actions):
        k = 1
        if self.step == 0:
            k = 3
        game = self.game

        # if game.all_in:  # No more betting to take place
        #     game.comm_cards(k)
        #     return
        self.reward += game.betting_round(avail_actions)

        game.reset_bets()

        if len(game.player_list) == 1:
            return

        game.comm_cards(k)  # Reveal cards after each betting round
        self.step += 1

    def test_main(self):
        pass

    def is_terminal(self):
        return True

    def is_chance(self):
        return True

    def evaluation(self):
        winner = self.game.calculate_winner()
        if winner == self.players[self.to_move]:
            return self.reward
        return -self.game.bets[self.players[self.to_move].uuid]

    def inf_set(self):
        return -1

    def play(self, action):
        return self
