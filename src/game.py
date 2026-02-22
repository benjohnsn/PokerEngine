from .deck import Deck

class Game:
    def __init__(self):
        self.players = ["Player 1", "Player 2"]
        self.deck = Deck()

    def run(self):
        print("Starting Game...")
        print("Players:", self.players)