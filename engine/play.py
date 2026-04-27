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

    while not game.isGameOver():
        showStacks(game)
        game.playOneHand()
        showStats(game)

    winner = game.getGameWinner()
    print(winner.name, "wins the game!")


def setupHumanPlayers(players):
    print("\n--- Player Setup ---")

    for player in players:
        if isinstance(player.controller, HumanController):
            name = input(f"Enter name for {player.name}: ").strip()

            if name:
                player.name = name


def showStacks(game):
    for player in game.players:
        print(player.name, "Stack:", player.stack)


def showStats(game):
    print("\n--- Stats ---")
    for player in game.players:
        print(
            player.name,
            f"Hands: {player.stats.hands}",
            f"VPIP: {player.stats.getVpipPct():.1f}%",
            f"PFR: {player.stats.getPfrPct():.1f}%",
            f"Agg: {player.stats.getAggressionPct():.1f}%"
        )


if __name__ == "__main__":
    main()
