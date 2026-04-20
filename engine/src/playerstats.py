class PlayerStats:
    def __init__(self):
        self.hands = 0

        self.vpip = 0
        self.vpipOpps = 0

        self.pfr = 0
        self.pfrOpps = 0

        self.bets = 0
        self.raises = 0
        self.calls = 0
        self.folds = 0

        self.showdowns = 0
        self.showdownWins = 0


    def getVpipPct(self):
        if self.vpipOpps == 0:
            return 0
        return (self.vpip / self.vpipOpps) * 100


    def getPfrPct(self):
        if self.pfrOpps == 0:
            return 0
        return (self.pfr / self.pfrOpps) * 100


    def getAggressionPct(self):
        aggressive = self.bets + self.raises
        total = self.bets + self.raises + self.calls

        if total == 0:
            return 0

        return (aggressive / total) * 100
