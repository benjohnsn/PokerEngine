class ScriptedController:
    def __init__(self, actions):
        self.actions = actions
        self.index = 0

    def getAction(self, game, player, validActions, amountToCall):
        if self.index >= len(self.actions):
            raise ValueError("No scripted actions left")

        action, targetBet = self.actions[self.index]
        self.index += 1

        return action, targetBet
