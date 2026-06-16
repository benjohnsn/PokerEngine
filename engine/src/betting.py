class BettingManager:
    def __init__(self, game):
        self.game = game


    def bettingRound(self, preflop=False):
        self.game.lastRaiser = None
        playersActed = set()

        if preflop:
            actingOrder = self.game.getPlayersInOrder(self.game.getUnderTheGunIndex())
        else:
            actingOrder = self.game.getPlayersInOrder((self.game.dealerIndex + 1) % len(self.game.getLivePlayers()))

        while True:
            for player in actingOrder:
                if player.folded:
                    continue

                if self.game.countActivePlayers() == 1:
                    return

                if self.game.lastRaiser and player == self.game.lastRaiser and len(playersActed) > 1:
                    return

                validActions = self.getValidActions(player)
                amountToCall = self.getAmountToCall(player)

                action, targetBet = player.controller.getAction(self.game, player, validActions, amountToCall)

                playersActed.add(player)
                self.applyAction(player, action, targetBet, preflop)

                if action == "raise":
                    playersActed = {player}

            if self.game.lastRaiser is None and self.isBettingRoundComplete():
                return


    def applyAction(self, player, action, targetBet=None, preflop=False):
        if action == "fold":
            self.fold(player)
            player.stats.folds += 1

        elif action == "check":
            self.check(player)

        elif action == "call":
            amountToCall = self.getAmountToCall(player)
            callAmount = min(amountToCall, player.stack)
            self.call(player)
            player.stats.calls += 1

            if preflop and callAmount > 0:
                player.didVpip = True

        elif action == "raise":
            if targetBet is None:
                raise ValueError("Raise amount required")

            wasBettingClosed = self.getHighestBet() == 0

            self.raiseTo(player, targetBet)

            if wasBettingClosed:
                player.stats.bets += 1
            else:
                player.stats.raises += 1

            if preflop:
                player.didVpip = True
                player.didPfr = True

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
        player.contribution += callAmount
        self.game.pot += callAmount


    def raiseTo(self, player, targetBet):
        if not self.isValidRaise(player, targetBet):
            raise ValueError("Invalid raise amount")

        additionalAmount = targetBet - player.currentBet
        raiseAmount = min(additionalAmount, player.stack)

        player.stack -= raiseAmount
        player.currentBet += raiseAmount
        player.contribution += raiseAmount
        self.game.pot += raiseAmount

        self.game.lastRaiser = player


    def isBettingRoundComplete(self):
        highestBet = 0

        for player in self.game.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            if player.currentBet > highestBet:
                highestBet = player.currentBet

        for player in self.game.players:
            if player.folded:
                continue
            if len(player.hand) == 0:
                continue
            if player.stack == 0:
                continue
            if player.currentBet != highestBet:
                return False

        return True


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


    def getHighestBet(self):
        highestBet = 0
        for player in self.game.players:
            if player.currentBet > highestBet:
                highestBet = player.currentBet
        return highestBet


    def getAmountToCall(self, player):
        return self.getHighestBet() - player.currentBet
