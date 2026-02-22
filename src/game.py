from .deck import Deck

class Game:
    def __init__(self):
        self.players = ["Player 1", "Player 2"]
        self.deck = Deck()
        self.player1Hand = []
        self.player2Hand = []

    def run(self):
        print("Starting Game...")
        print("Players:", self.players)
        
        self.deck.shuffle()
        
        self.player1Hand.append(self.deck.deal())
        self.player1Hand.append(self.deck.deal())
        self.player2Hand.append(self.deck.deal())
        self.player2Hand.append(self.deck.deal())

        print(self.player1Hand)
        print(self.player2Hand)