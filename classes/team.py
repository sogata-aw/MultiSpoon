from classes import player as pl

class Team():
    players: list[pl.Player] = []
    rankSum: int = 0
    deviation: float = 0

    def __init__(self, players: list[pl.Player]) -> None:
        self.players = players
        self.rankSum = sum([p.rank for p in self.players])

    def __repr__(self) -> str:
        s = f"\nTeam Total Rank : {self.rankSum}\nDeviation = {self.deviation}\nPlayers : \n"
        for player in self.players:
            s += f"\t{player}\n"
        return s + "\n"

    def update(self):
        self.rankSum = sum([p.rank for p in self.players])