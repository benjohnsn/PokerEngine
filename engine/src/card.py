from .constants import RANK_TO_VALUE
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_TO_VALUE[rank]

    def __str__(self):
        return self.rank + self.suit
    
    def __repr__(self):
        return self.rank + self.suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
