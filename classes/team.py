from classes.player import Player


class Team:
    def __init__(self, limit):
        self.players: list[Player] = []
        self.power: int = 0
        self.limit = limit

    def __repr__(self):
        return f"[power : {self.power}, players : {self.players}]"

    def is_full(self):
        return len(self.players) >= self.limit

    def add_player(self, player: Player):
        self.players.append(player)
        self.power += player.power
        player.team = self
