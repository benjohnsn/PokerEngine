from .player import Player
from .deck import Deck
from .evaluator import Evaluator

class Game:
    def __init__(self):
        self.players = [Player("Hero"), Player("Villain")]
        self.deck = Deck()
        self.evaluator = Evaluator()

        self.board = []
        self.pot = 0
        self.lastRaiser = None


    def run(self):
        self.newHand()
        self.deck.shuffle()
        self.postBlinds()

        self.dealHands()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealFlop()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealTurn()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealRiver()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            return
        self.resetCurrentBets()

        self.showState()
        self.showdown()


    def newHand(self):
        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.lastRaiser = None

        for player in self.players:
            player.newHand()


    def postBlinds(self):
        smallBlind = 5
        bigBlind = 10

        sbPlayer = self.players[0]
        bbPlayer = self.players[1]

        sbPlayer.stack -= smallBlind
        sbPlayer.currentBet = smallBlind

        bbPlayer.stack -= bigBlind
        bbPlayer.currentBet = bigBlind

        self.pot += smallBlind + bigBlind


    def bettingRound(self):
        self.lastRaiser = None
        playersActed = set()

        while True:
            for player in self.players:
                if player.folded:
                    continue

                if self.countActivePlayers() == 1:
                    return
                
                action = self.getPlayerAction(player)
                playersActed.add(player)

                if action == "fold":
                    self.fold(player)
                    print(player.name, "folds")

                elif action == "check":
                    self.check(player)
                    print(player.name, "checks")

                elif action == "call":
                    amountToCall = self.getAmountToCall(player)
                    self.call(player)
                    print(player.name, "calls", amountToCall)

                elif action == "raise":
                    targetBet = int(input("Enter total bet amount: "))
                    self.raiseTo(player, targetBet)
                    playersActed = {player}
                    print(player.name, "raises to", targetBet)

                if self.lastRaiser and player == self.lastRaiser and len(playersActed) > 1:
                    return
            
            if self.lastRaiser is None and self.isBettingRoundComplete():
                return


    def getPlayerAction(self, player):
        amountToCall = self.getAmountToCall(player)

        if self.canCheck(player):
            validActions = ["check", "fold"]
            prompt = f"{player.name} - check or fold: "
        elif self.canCall(player):
            validActions = ["call", "raise", "fold"]
            prompt = f"{player.name} - call {amountToCall}, raise or fold: "
        else:
            validActions = ["fold"]
            prompt = f"{player.name} - fold: "

        while True:
            action = input(prompt).strip().lower()
            if action in validActions:
                return action
            print("Invalid action. Try again.")


    def fold(self, player):
        player.folded = True


    def check(self, player):
        if not self.canCheck(player):
            raise ValueError("Invalid check")


    def call(self, player):
        if not self.canCall(player):
            raise ValueError("Invalid call")

        amountToCall = self.getAmountToCall(player)
        callAmount = min(amountToCall, player.stack)

        player.stack -= callAmount
        player.currentBet += callAmount
        self.pot += callAmount


    def raiseTo(self, player, targetBet):
        if not self.isValidRaise(player, targetBet):
            raise ValueError("Invalid raise amount")

        additionalAmount = targetBet - player.currentBet
        raiseAmount = min(additionalAmount, player.stack)

        player.stack -= raiseAmount
        player.currentBet += raiseAmount
        self.pot += raiseAmount

        self.lastRaiser = player


    def canCheck(self, player):
        return self.getAmountToCall(player) == 0


    def canCall(self, player):
        amountToCall = self.getAmountToCall(player)
        return amountToCall > 0 and player.stack > 0


    def isValidRaise(self, player, targetBet):
        highestBet = self.getHighestBet()

        if player.stack <= 0:
            return False

        if targetBet <= highestBet:
            return False

        maxBet = player.currentBet + player.stack
        if targetBet > maxBet:
            return False

        if targetBet == maxBet:
            return True

        minRaiseTo = highestBet * 2 if highestBet > 0 else 10
        if targetBet < minRaiseTo:
            return False

        return True


    def getAmountToCall(self, player):
        highestBet = self.getHighestBet()
        return highestBet - player.currentBet


    def getHighestBet(self):
        highestBet = 0
        for player in self.players:
            if player.currentBet > highestBet:
                highestBet = player.currentBet

        return highestBet


    def isBettingRoundComplete(self):
        highestBet = 0

        for player in self.players:
            if not player.folded and player.currentBet > highestBet:
                highestBet = player.currentBet

        for player in self.players:
            if player.folded:
                continue
            if player.stack == 0:
                continue
            if player.currentBet != highestBet:
                return False

        return True


    def resetCurrentBets(self):
        for player in self.players:
            player.currentBet = 0


    def countActivePlayers(self):
        count = 0
        for player in self.players:
            if not player.folded:
                count += 1
        return count


    def getRemainingPlayer(self):
        for player in self.players:
            if not player.folded:
                return player


    def handFoldWin(self):
        winner = self.getRemainingPlayer()
        self.awardPot([winner])
        print(winner.name, "wins (opponent folded)")


    def showdown(self):
        p1Score = self.evaluator.evaluateHand(self.players[0].hand + self.board)
        p2Score = self.evaluator.evaluateHand(self.players[1].hand + self.board)

        if p1Score > p2Score:
            self.awardPot([self.players[0]])
            print(self.players[0], "wins with", self.evaluator.formatHand(p1Score))
        elif p2Score > p1Score:
            self.awardPot([self.players[1]])
            print(self.players[1], "wins with", self.evaluator.formatHand(p2Score))
        else:
            self.awardPot(self.players)
            print("Tie!", self.evaluator.formatHand(p1Score))


    def awardPot(self, winners):
        share = self.pot // len(winners)
        remainder = self.pot % len(winners)

        for player in winners:
            player.stack += share

        # distribute remaining chips clockwise from left of the dealer (poker rule for uneven pot)
        for i in range(remainder):
            winners[i].stack += 1

        self.pot = 0


    def dealHands(self):
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())


    def burn(self):
        self.deck.deal()


    def dealFlop(self):
        for _ in range(3):
            self.board.append(self.deck.deal())


    def dealTurn(self):
        self.board.append(self.deck.deal())


    def dealRiver(self):
        self.board.append(self.deck.deal())


    def showState(self):
        for player in self.players:
            print(player.name, player.hand, "Stack:", player.stack, "Bet:", player.currentBet)
        print("Board:", self.board)
        print("Pot:", self.pot)
