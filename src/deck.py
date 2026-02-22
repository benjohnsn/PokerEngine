import random
from .constants import SUITS, RANKS
from .card import Card

class Deck:
    def __init__(self):
        self.cards = []
        for suit in SUITS:
            for rank in RANKS:
                card = Card(rank, suit)
                self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()
