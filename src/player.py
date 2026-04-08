class Player:
    def __init__(self, name, stack=1000):
        self.name = name
        self.hand = []
        self.stack = stack
        self.currentBet = 0
        self.folded = False

    def newHand(self):
        self.hand = []
        self.currentBet = 0
        self.folded = False

    def __repr__(self):
        return f"{self.name}: {self.hand}"