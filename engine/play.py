import json

from engine.src.game import Game
from engine.src.player import Player
from engine.src.controllers import CLIHumanController, TightAggressiveController

def main():
    players = [
        Player("Player 1", controller=CLIHumanController()),
        Player("Player 2", controller=TightAggressiveController()),
        Player("Player 3", controller=TightAggressiveController()),
        Player("Player 4", controller=TightAggressiveController()),
        Player("Player 5", controller=TightAggressiveController()),
        Player("Player 6", controller=TightAggressiveController())
    ]

    setupHumanPlayers(players)

    game = Game(players)
    game.loadStats()

    while not game.isGameOver():
        game.step()

    winner = game.getGameWinner()
    print(winner.name, "wins the game!")


def setupHumanPlayers(players):
    print("\n--- Player Setup ---")

    for player in players:
        if isinstance(player.controller, CLIHumanController):
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


def saveStats(game):
        path = "engine/data/profiles.json"

        data = {}

        for player in game.players:
            if not isinstance(player.controller, HumanController):
                continue
            
            data[player.name] = {
                "hands": player.stats.hands,
                "vpip": player.stats.vpip,
                "vpipOpps": player.stats.vpipOpps,
                "pfr": player.stats.pfr,
                "pfrOpps": player.stats.pfrOpps,
                "bets": player.stats.bets,
                "raises": player.stats.raises,
                "calls": player.stats.calls,
                "folds": player.stats.folds,
                "showdowns": player.stats.showdowns,
                "showdownWins": player.stats.showdownWins
            }

        with open(path, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
