import random
import time

class RandomController:
    def getAction(self, game, player, validActions, amountToCall):

        time.sleep(random.uniform(0.1, 5))
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