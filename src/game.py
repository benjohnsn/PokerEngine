from .player import Player
from .deck import Deck
from .betting import BettingManager
from .evaluator import Evaluator
from .controllers import HumanController

class Game:
    def __init__(self):
        self.players = [
            Player("Player 1", controller=HumanController()),
            Player("Player 2", controller=HumanController()),
            Player("Player 3", controller=HumanController()),
            Player("Player 4", controller=HumanController()),
            Player("Player 5", controller=HumanController()),
            Player("Player 6", controller=HumanController())
        ]
        self.deck = Deck()
        self.bettingManager = BettingManager(self)
        self.evaluator = Evaluator()

        self.board = []
        self.pot = 0
        self.lastRaiser = None
        self.dealerIndex = 0


    def run(self):
        while not self.isGameOver():
            self.playHand()
            self.rotateDealer()
            self.showStacks()

        winner = self.getGameWinner()
        print(winner.name, "wins the game!")


    def playHand(self):
        self.newHand()
        self.deck.shuffle()
        self.postBlinds()

        self.dealHands()
        self.bettingRound(preflop=True)
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


    def getPlayersInOrder(self, startIndex):
        livePlayers = self.getLivePlayers()
        orderedPlayers = []

        for i in range(len(livePlayers)):
            index = (startIndex + i) % len(livePlayers)
            orderedPlayers.append(livePlayers[index])

        return orderedPlayers


    def getSmallBlindIndex(self):
        livePlayers = self.getLivePlayers()
        return (self.dealerIndex + 1) % len(livePlayers)


    def getBigBlindIndex(self):
        livePlayers = self.getLivePlayers()
        return (self.dealerIndex + 2) % len(livePlayers)


    def getUnderTheGunIndex(self):
        livePlayers = self.getLivePlayers()
        return (self.dealerIndex + 3) % len(livePlayers)


    def rotateDealer(self):
        livePlayers = self.getLivePlayers()
        self.dealerIndex = (self.dealerIndex + 1) % len(livePlayers)


    def getLivePlayers(self):
        livePlayers = []
        for player in self.players:
            if player.stack > 0:
                livePlayers.append(player)
        return livePlayers


    def postBlinds(self):
        smallBlind = 5
        bigBlind = 10
        livePlayers = self.getLivePlayers()

        sbPlayer = livePlayers[self.getSmallBlindIndex()]
        bbPlayer = livePlayers[self.getBigBlindIndex()]

        sbPosted = min(smallBlind, sbPlayer.stack)
        bbPosted = min(bigBlind, bbPlayer.stack)

        sbPlayer.stack -= sbPosted
        sbPlayer.currentBet = sbPosted

        bbPlayer.stack -= bbPosted
        bbPlayer.currentBet = bbPosted

        self.pot += sbPosted + bbPosted


    def bettingRound(self, preflop=False):
        self.bettingManager.bettingRound(preflop)


    def fold(self, player):
        self.bettingManager.fold(player)


    def check(self, player):
        self.bettingManager.check(player)


    def call(self, player):
        self.bettingManager.call(player)


    def raiseTo(self, player, targetBet):
        self.bettingManager.raiseTo(player, targetBet)


    def applyAction(self, player, action, targetBet=None):
        self.bettingManager.applyAction(player, action, targetBet)


    def getValidActions(self, player):
        return self.bettingManager.getValidActions(player)


    def canCheck(self, player):
        return self.bettingManager.canCheck(player)


    def canCall(self, player):
        return self.bettingManager.canCall(player)


    def isRaiseAvailable(self, player):
        return self.bettingManager.isRaiseAvailable(player)


    def isValidRaise(self, player, targetBet):
        return self.bettingManager.isValidRaise(player, targetBet)


    def getAmountToCall(self, player):
        return self.bettingManager.getAmountToCall(player)


    def getHighestBet(self):
        return self.bettingManager.getHighestBet()


    def isBettingRoundComplete(self):
        return self.bettingManager.isBettingRoundComplete()


    def resetCurrentBets(self):
        for player in self.players:
            player.currentBet = 0


    def countActivePlayers(self):
        count = 0
        for player in self.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            count += 1
        return count


    def getRemainingPlayer(self):
        for player in self.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            return player


    def isGameOver(self):
        return len(self.getLivePlayers()) == 1


    def getGameWinner(self):
        livePlayers = self.getLivePlayers()
        return livePlayers[0]


    def showStacks(self):
        for player in self.players:
            print(player.name, "Stack:", player.stack)


    def handFoldWin(self):
        winner = self.getRemainingPlayer()
        self.awardPot([winner])
        print(winner.name, "wins by everyone folding")


    def showdown(self):
        activePlayers = []
        bestScore = None

        for player in self.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue

            score = self.evaluator.evaluateHand(player.hand + self.board)
            activePlayers.append((player, score))

            if bestScore is None or score > bestScore:
                bestScore = score

        winners = []
        for player, score in activePlayers:
            if score == bestScore:
                winners.append(player)

        self.awardPot(winners)

        if len(winners) == 1:
            print(winners[0].name, "wins with", self.evaluator.formatHand(bestScore))
        else:
            winnerNames = []
            for player in winners:
                winnerNames.append(player.name)
            print("Tie between", ", ".join(winnerNames), "with", self.evaluator.formatHand(bestScore))


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
        livePlayers = self.getLivePlayers()
        for _ in range(2):
            for player in livePlayers:
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
