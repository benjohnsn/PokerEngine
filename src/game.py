from .player import Player
from .deck import Deck
from .evaluator import Evaluator

class Game:
    def __init__(self):
        self.players = [Player("Player 1"), Player("Player 2"), Player("Player 3"), Player("Player 4"), Player("Player 5"), Player("Player 6")]
        self.deck = Deck()
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
        self.lastRaiser = None
        playersActed = set()

        if preflop:
            actingOrder = self.getPlayersInOrder(self.getUnderTheGunIndex())
        else:
            actingOrder = self.getPlayersInOrder((self.dealerIndex + 1) % len(self.getLivePlayers()))

        while True:
            for player in actingOrder:
                if player.folded:
                    continue

                if self.countActivePlayers() == 1:
                    return
                
                action = self.getPlayerAction(player)
                playersActed.add(player)

                targetBet = None
                if action == "raise":
                    targetBet = int(input("Enter total bet amount: "))

                self.applyAction(player, action, targetBet)

                if action == "raise":
                    playersActed = {player}

                if self.lastRaiser and player == self.lastRaiser and len(playersActed) > 1:
                    return
            
            if self.lastRaiser is None and self.isBettingRoundComplete():
                return


    def getPlayerAction(self, player):
        validActions = self.getValidActions(player)
        amountToCall = self.getAmountToCall(player)

        if validActions == ["fold"]:
            prompt = f"{player.name} - fold: "
        elif validActions == ["check", "raise", "fold"]:
            prompt = f"{player.name} - check, raise or fold: "
        elif validActions == ["check", "fold"]:
            prompt = f"{player.name} - check or fold: "
        elif validActions == ["call", "raise", "fold"]:
            prompt = f"{player.name} - call {amountToCall}, raise or fold: "
        elif validActions == ["call", "fold"]:
            prompt = f"{player.name} - call {amountToCall} or fold: "
        else:
            raise ValueError("Unexpected valid actions")

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


    def applyAction(self, player, action, targetBet=None):
        if action == "fold":
            self.fold(player)

        elif action == "check":
            self.check(player)

        elif action == "call":
            self.call(player)

        elif action == "raise":
            if targetBet is None:
                raise ValueError("Raise amount required")

            self.raiseTo(player, targetBet)

        else:
            raise ValueError("Invalid action")


    def getValidActions(self, player):
        validActions = []

        if player.folded:
            return validActions

        if self.canCheck(player):
            validActions.append("check")
        elif self.canCall(player):
            validActions.append("call")

        if self.isRaiseAvailable(player):
            validActions.append("raise")

        validActions.append("fold")
        return validActions


    def canCheck(self, player):
        return self.getAmountToCall(player) == 0


    def canCall(self, player):
        amountToCall = self.getAmountToCall(player)
        return amountToCall > 0 and player.stack > 0


    def isRaiseAvailable(self, player):
        return player.stack > self.getAmountToCall(player)


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
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            if player.currentBet > highestBet:
                highestBet = player.currentBet

        for player in self.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
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
