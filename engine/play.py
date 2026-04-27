from engine.src.game import Game
from engine.src.player import Player
from engine.src.controllers import RandomController, HumanController, TightAggressiveController

def main():
    players = [
        Player("Player 1", controller=HumanController()),
        Player("Player 2", controller=TightAggressiveController()),
        Player("Player 3", controller=TightAggressiveController()),
        Player("Player 4", controller=TightAggressiveController()),
        Player("Player 5", controller=TightAggressiveController()),
        Player("Player 6", controller=TightAggressiveController())
    ]

    setupHumanPlayers(players)

    game = Game(players)
    game.run()


def setupHumanPlayers(players):
    print("\n--- Player Setup ---")

    for player in players:
        if isinstance(player.controller, HumanController):
            name = input(f"Enter name for {player.name}: ").strip()

            if name:
                player.name = name


def showStacks(self):
    for player in self.players:
        print(player.name, "Stack:", player.stack)


if __name__ == "__main__":
    main()
