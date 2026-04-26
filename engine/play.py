from engine.src.game import Game
from engine.src.player import Player
from engine.src.controllers import RandomController, HumanController,  TightAggressiveController

def main():
    players = [
        Player("Player 1", controller=HumanController()),
        Player("Player 2", controller=TightAggressiveController()),
        Player("Player 3", controller=TightAggressiveController()),
        Player("Player 4", controller=TightAggressiveController()),
        Player("Player 5", controller=TightAggressiveController()),
        Player("Player 6", controller=TightAggressiveController())
    ]

    game = Game()
    game.run()

if __name__ == "__main__":
    main()
