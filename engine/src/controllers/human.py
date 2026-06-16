class HumanController:
    def __init__(self):
        self.pendingAction = None
        self.pendingTargetBet = None

    def setAction(self, action, targetBet=None):
        self.pendingAction = action
        self.pendingTargetBet = targetBet

    def getAction(self, game, player, validActions, amountToCall):
        if self.pendingAction is None:
            return "fold", None

        action = self.pendingAction
        targetBet = self.pendingTargetBet

        self.pendingAction = None
        self.pendingTargetBet = None

        if action not in validActions:
            return "fold", None

        if action == "raise":
            return action, targetBet

        return action, None