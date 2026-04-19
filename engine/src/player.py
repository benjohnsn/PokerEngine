from .playerstats import PlayerStats

class Player:
    def __init__(self, name, stack=1000, controller=None):
        self.name = name
        self.stack = stack
        self.controller = controller
        self.stats = PlayerStats()
    
        self.hand = []
        self.currentBet = 0
        self.contribution = 0
        self.folded = False

    def newHand(self):
        self.hand = []
        self.currentBet = 0
        self.contribution = 0
        self.folded = False

    def __repr__(self):
        return f"{self.name}: {self.hand}"
