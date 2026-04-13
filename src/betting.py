class BettingManager:
    def __init__(self, game):
        self.game = game


    def getHighestBet(self):
        highestBet = 0
        for player in self.game.players:
            if player.currentBet > highestBet:
                highestBet = player.currentBet
        return highestBet


    def getAmountToCall(self, player):
        return self.getHighestBet() - player.currentBet


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

        # all-in is always allowed
        if targetBet == maxBet:
            return True

        minRaiseTo = highestBet * 2 if highestBet > 0 else 10
        if targetBet < minRaiseTo:
            return False

        return True


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
        self.game.pot += callAmount


    def raiseTo(self, player, targetBet):
        if not self.isValidRaise(player, targetBet):
            raise ValueError("Invalid raise amount")

        additionalAmount = targetBet - player.currentBet
        raiseAmount = min(additionalAmount, player.stack)

        player.stack -= raiseAmount
        player.currentBet += raiseAmount
        self.game.pot += raiseAmount

        self.game.lastRaiser = player


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

                validActions = self.getValidActions(player)
                amountToCall = self.getAmountToCall(player)

                action, targetBet = player.controller.getAction(self.game, player, validActions, amountToCall)
                playersActed.add(player)

                self.applyAction(player, action, targetBet)

                if action == "raise":
                    playersActed = {player}

                if (self.game.lastRaiser and player == self.game.lastRaiser and len(playersActed) > 1):
                    return

            if self.game.lastRaiser is None and self.isBettingRoundComplete():
                return
