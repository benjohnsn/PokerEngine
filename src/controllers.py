import random
class HumanController:
    def getAction(self, game, player, validActions, amountToCall):
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

            if action not in validActions:
                print("Invalid action. Try again.")
                continue

            if action == "raise":
                targetBet = int(input("Enter total bet amount: "))
                return action, targetBet

            return action, None

class RandomController:
    def getAction(self, game, player, validActions, amountToCall):
        action = random.choice(validActions)

        if action == "raise":
            targetBets = []
            minBet = player.currentBet + 1
            maxBet = player.currentBet + player.stack

            for targetBet in range(minBet, maxBet + 1):
                if game.isValidRaise(player, targetBet):
                    targetBets.append(targetBet)
            
            if not targetBets:
                return "fold", None

            targetBet = random.choice(targetBets)

            return action, targetBet

        return action, None

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