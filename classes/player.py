class Player():
    name: str = ""
    rank: int = 0

    def __init__(self, name: str, rank: int) -> None:
        self.name = name
        self.rank = rank

    def __repr__(self) -> str:
        return f"{self.name} : {self.rank}"