class Player:
    def __init__(self, name, power):
        self.name = name
        self.power = power
        self.team = None

    def __int__(self):
        return self.power

    def __repr__(self):
        return f"{self.name} : {self.power}"

