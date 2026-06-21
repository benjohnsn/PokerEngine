class CLIHumanController:
    def getAction(self, game, player, validActions, amountToCall):
        while True:
            print()
            print("Player:", player.name)
            print("Hand:", player.hand)
            print("Board:", game.board)
            print("Pot:", game.pot)
            print("Stack:", player.stack)
            print("To call:", amountToCall)
            print("Valid actions:", validActions)

            action = input("> ").strip().lower()

            if action not in validActions:
                print("Invalid action")
                continue

            if action == "raise":
                try:
                    targetBet = int(input("Raise to: "))

                    if not game.isValidRaise(player, targetBet):
                        print("Invalid raise amount")
                        continue

                    return "raise", targetBet

                except ValueError:
                    print("Enter a number")
                    continue

            return action, None