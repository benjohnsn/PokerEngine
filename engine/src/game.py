import os
import json
import time

from .player import Player
from .deck import Deck
from .betting import BettingManager
from .evaluator import Evaluator
from .controllers import HumanController, RandomController, TightAggressiveController

class Game:
    def __init__(self):
        self.players = [
            Player("Player 1", controller=HumanController()),
            Player("Player 2", controller=TightAggressiveController()),
            Player("Player 3", controller=TightAggressiveController()),
            Player("Player 4", controller=TightAggressiveController()),
            Player("Player 5", controller=TightAggressiveController()),
            Player("Player 6", controller=TightAggressiveController())
        ]
        self.deck = Deck()
        self.bettingManager = BettingManager(self)
        self.evaluator = Evaluator()

        self.board = []
        self.pot = 0
        self.lastRaiser = None
        self.dealerIndex = 0


    def run(self):
        self.setupHumanPlayers()
        self.loadStats()

        while not self.isGameOver():
            time.sleep(2)
            self.playHand()
            self.rotateDealer()
            self.showStacks()
            self.showStats()

        self.saveStats()
        winner = self.getGameWinner()
        print(winner.name, "wins the game!")


    def setupHumanPlayers(self):
        print("\n--- Player Setup ---")

        for player in self.players:
            if isinstance(player.controller, HumanController):
                name = input(f"Enter name for {player.name}: ").strip()

                if name:
                    player.name = name


    def playHand(self):
        print("\n--- New Hand ---")
        self.showStacks()

        self.newHand()
        self.deck.shuffle()
        self.postBlinds()

        self.dealHands()
        print("\n--- Preflop ---")
        self.showState()
        self.bettingRound(preflop=True)
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            self.recordHandStats()
            self.saveStats()
            return
        if self.shouldRunoutBoard():
            self.runoutBoard()
            self.recordHandStats()
            self.saveStats()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealFlop()
        print("\n--- Flop ---")
        self.showState()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            self.recordHandStats()
            self.saveStats()
            return
        if self.shouldRunoutBoard():
            self.runoutBoard()
            self.recordHandStats()
            self.saveStats()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealTurn()
        print("\n--- Turn ---")
        self.showState()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            self.recordHandStats()
            self.saveStats()
            return
        if self.shouldRunoutBoard():
            self.runoutBoard()
            self.recordHandStats()
            self.saveStats()
            return
        self.resetCurrentBets()

        self.burn()
        self.dealRiver()
        print("\n--- River ---")
        self.showState()
        self.bettingRound()
        if self.countActivePlayers() == 1:
            self.handFoldWin()
            self.recordHandStats()
            self.saveStats()
            return
        self.resetCurrentBets()

        print("\n--- Showdown ---")
        self.showState()
        self.showdown()
        self.recordHandStats()
        self.saveStats()


    def newHand(self):
        self.deck = Deck()
        self.board = []
        self.pot = 0
        self.lastRaiser = None

        for player in self.players:
            player.newHand()
            player.stats.hands += 1


    def recordHandStats(self):
        for player in self.players:
            if len(player.hand) == 0:
                continue

            player.stats.vpipOpps += 1
            player.stats.pfrOpps += 1

            if player.didVpip:
                player.stats.vpip += 1

            if player.didPfr:
                player.stats.pfr += 1


    def loadStats(self):
        path = "engine/data/profiles.json"

        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            data = json.load(f)

        for player in self.players:
            if player.name not in data:
                continue

            statsData = data[player.name]

            player.stats.hands = statsData.get("hands", 0)
            player.stats.vpip = statsData.get("vpip", 0)
            player.stats.vpipOpps = statsData.get("vpipOpps", 0)
            player.stats.pfr = statsData.get("pfr", 0)
            player.stats.pfrOpps = statsData.get("pfrOpps", 0)
            player.stats.bets = statsData.get("bets", 0)
            player.stats.raises = statsData.get("raises", 0)
            player.stats.calls = statsData.get("calls", 0)
            player.stats.folds = statsData.get("folds", 0)
            player.stats.showdowns = statsData.get("showdowns", 0)
            player.stats.showdownWins = statsData.get("showdownWins", 0)


    def saveStats(self):
        path = "engine/data/profiles.json"

        data = {}

        for player in self.players:
            if not isinstance(player.controller, HumanController):
                continue
            
            data[player.name] = {
                "hands": player.stats.hands,
                "vpip": player.stats.vpip,
                "vpipOpps": player.stats.vpipOpps,
                "pfr": player.stats.pfr,
                "pfrOpps": player.stats.pfrOpps,
                "bets": player.stats.bets,
                "raises": player.stats.raises,
                "calls": player.stats.calls,
                "folds": player.stats.folds,
                "showdowns": player.stats.showdowns,
                "showdownWins": player.stats.showdownWins
            }

        with open(path, "w") as f:
            json.dump(data, f, indent=4)


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


    def getActivePlayers(self):
        active = []
        for player in self.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            active.append(player)
        return active


    def shouldRunoutBoard(self):
        activePlayers = self.getActivePlayers()

        playersWhoCanAct = 0
        for player in activePlayers:
            if player.stack > 0:
                playersWhoCanAct += 1

        return len(activePlayers) > 1 and playersWhoCanAct <= 1


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
        sbPlayer.contribution += sbPosted

        bbPlayer.stack -= bbPosted
        bbPlayer.currentBet = bbPosted
        bbPlayer.contribution += bbPosted

        self.pot += sbPosted + bbPosted

        print(sbPlayer.name, "posts small blind", sbPosted)
        print(bbPlayer.name, "posts big blind", bbPosted)
        print("Pot:", self.pot)


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
        return len(self.getActivePlayers())


    def getRemainingPlayer(self):
        activePlayers = self.getActivePlayers()
        return activePlayers[0]


    def isGameOver(self):
        return len(self.getLivePlayers()) == 1


    def getGameWinner(self):
        livePlayers = self.getLivePlayers()
        return livePlayers[0]


    def showStacks(self):
        for player in self.players:
            print(player.name, "Stack:", player.stack)


    def showStats(self):
        print("\n--- Stats ---")
        for player in self.players:
            print(
                player.name,
                f"Hands: {player.stats.hands}",
                f"VPIP: {player.stats.getVpipPct():.1f}%",
                f"PFR: {player.stats.getPfrPct():.1f}%",
                f"Agg: {player.stats.getAggressionPct():.1f}%"
            )


    def handFoldWin(self):
        winner = self.getRemainingPlayer()
        winner.stack += self.pot
        self.pot = 0
        print(winner.name, "wins by everyone folding")


    def showdown(self):
        activePlayers = self.getActivePlayers()

        for player in activePlayers:
            player.stats.showdowns += 1
            score = self.evaluator.evaluateHand(player.hand + self.board)
            print(player.name, player.hand, "->", self.evaluator.formatHand(score))

        bestScore = None
        winners = []

        for player in activePlayers:
            score = self.evaluator.evaluateHand(player.hand + self.board)

            if bestScore is None or score > bestScore:
                bestScore = score
                winners = [player]
            elif score == bestScore:
                winners.append(player)

        for player in winners:
            player.stats.showdownWins += 1

        self.awardPot()

        if len(winners) == 1:
            print(winners[0].name, "wins with", self.evaluator.formatHand(bestScore))
        else:
            winnerNames = []
            for player in winners:
                winnerNames.append(player.name)
            print("Tie between", ", ".join(winnerNames), "with", self.evaluator.formatHand(bestScore))


    def awardPot(self):
        # Start with only players who have put chips into the pot this hand.
        remainingPlayers = []
        for player in self.players:
            if player.contribution > 0:
                remainingPlayers.append(player)

        # Keep creating pots until all contribution has been accounted for.
        while remainingPlayers:
            # Find the smallest remaining contribution.
            # This defines the next "layer" of the pot.
            smallestContribution = min(player.contribution for player in remainingPlayers)

            # Everyone still in remainingPlayers contributes this layer.
            potPlayers = remainingPlayers[:]
            potSize = smallestContribution * len(potPlayers)

            # Only players who have not folded can win this pot.
            eligiblePlayers = []
            for player in potPlayers:
                if not player.folded:
                    eligiblePlayers.append(player)

            # Find the best hand among players eligible to win this pot.
            bestScore = None
            winners = []

            for player in eligiblePlayers:
                score = self.evaluator.evaluateHand(player.hand + self.board)

                if bestScore is None or score > bestScore:
                    bestScore = score
                    winners = [player]
                elif score == bestScore:
                    winners.append(player)

            # Split this pot equally among the winners.
            share = potSize // len(winners)
            remainder = potSize % len(winners)

            for player in winners:
                player.stack += share

            # Give any leftover chips one by one to the first winners.
            for i in range(remainder):
                winners[i].stack += 1

            # Remove this contribution layer from every player still being considered.
            for player in remainingPlayers:
                player.contribution -= smallestContribution

            # Keep only players who still have contribution left for future side pots.
            newRemainingPlayers = []
            for player in remainingPlayers:
                if player.contribution > 0:
                    newRemainingPlayers.append(player)

            remainingPlayers = newRemainingPlayers

        # All pot layers have now been awarded.
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


    def runoutBoard(self):
        while len(self.board) < 5:
            self.burn()

            if len(self.board) == 0:
                self.dealFlop()
            elif len(self.board) == 3:
                self.dealTurn()
            elif len(self.board) == 4:
                self.dealRiver()

        print("\n--- Runout ---")
        self.showState()
        self.showdown()


    def showState(self):
        for player in self.players:
            if isinstance(player.controller, HumanController):
                handDisplay = player.hand
            else:
                handDisplay = ["??", "??"]

            print(player.name, handDisplay, "Stack:", player.stack, "Bet:", player.currentBet)

        print("Board:", self.board)
        print("Pot:", self.pot)
