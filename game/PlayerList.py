class PlayerList:
    """
    Mutable object that reflects the number of players involved in a game
    """
    def __init__(self, players):
        self.rotation = [x for x in players]
        self.pos = 0
        self.visited = 0

    def remove(self, player):
        self.rotation.remove(player)
        self.pos = max(self.pos - 1, 0)
        self.visited -= 1

    def next_player(self):
        player = self.rotation[self.pos]
        self.pos = (self.pos + 1) % len(self.rotation)
        self.visited += 1
        return player

    def visited_all(self):
        return self.visited >= len(self.rotation) or len(self.rotation) <= 1

    def duplicate(self):
        copy = PlayerList(self.rotation)
        copy.pos = self.pos
        copy.visited = self.visited
        return copy

    def __len__(self):
        return len(self.rotation)
