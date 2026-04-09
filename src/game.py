from .player import Player
from .deck import Deck
from .evaluator import Evaluator

class Game:
    def __init__(self):
        self.players = [Player("Hero"), Player("Villain")]
        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.evaluator = Evaluator()


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
        self.board = []
        self.deck = Deck()
        self.pot = 0
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


    def getAmountToCall(self, player):
        highestBet = 0

        for otherPlayer in self.players:
            if otherPlayer.currentBet > highestBet:
                highestBet = otherPlayer.currentBet

        return highestBet - player.currentBet


    def call(self, player):
        amountToCall = self.getAmountToCall(player)
        player.stack -= amountToCall
        player.currentBet += amountToCall
        self.pot += amountToCall


    def check(self, player):
        pass


    def fold(self, player):
        player.folded = True


    def bettingRound(self):
        for player in self.players:
            if player.folded:
                continue
            amountToCall = self.getAmountToCall(player)
            if amountToCall == 0:
                self.check(player)
                print(player.name, "checks")
            else:
                self.call(player)
                print(player.name, "calls", amountToCall)


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
        print(winner.name, "wins (opponent folded)")


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


    def showdown(self):
        p1Score = self.evaluator.evaluateHand(self.players[0].hand + self.board)
        p2Score = self.evaluator.evaluateHand(self.players[1].hand + self.board)

        if p1Score > p2Score:
            print(self.players[0], "wins with", self.evaluator.formatHand(p1Score))
        elif p2Score > p1Score:
            print(self.players[1], "wins with", self.evaluator.formatHand(p2Score))
        else:
            print("Tie!", self.evaluator.formatHand(p1Score))
