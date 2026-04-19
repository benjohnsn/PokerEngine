import random

from .deck import Deck
from .evaluator import Evaluator

class EquityCalculator:
    def __init__(self):
        self.evaluator = Evaluator()


    def simulateOnce(self, heroHand, board, numOpponents):
        if len(heroHand) != 2:
            raise ValueError("Hero hand must contain exactly 2 cards.")

        if len(board) > 5:
            raise ValueError("Board cannot contain more than 5 cards.")

        if numOpponents < 1:
            raise ValueError("There must be at least 1 opponent.")

        if numOpponents > 5:
            raise ValueError("Maximum supported opponents is 5.")

        deck = Deck()
        knownCards = heroHand + board

        # remove hero + board cards
        deck.cards = self.removeKnownCards(deck.cards, knownCards)

        deck.shuffle()

        # deal opponent hands
        opponentHands = []
        for _ in range(numOpponents):
            opponentHands.append([deck.deal(), deck.deal()])

        # complete the board
        fullBoard = board[:]
        while len(fullBoard) < 5:
            fullBoard.append(deck.deal())

        # evaluate hero
        heroScore = self.evaluator.evaluateHand(heroHand + fullBoard)

        # evaluate opponents
        bestOpponentScore = None

        for opponentHand in opponentHands:
            opponentScore = self.evaluator.evaluateHand(opponentHand + fullBoard)

            if bestOpponentScore is None or opponentScore > bestOpponentScore:
                bestOpponentScore = opponentScore

        # compare results
        if heroScore > bestOpponentScore:
            return "win"
        elif heroScore == bestOpponentScore:
            return "tie"
        else:
            return "loss"


    def removeKnownCards(self, deckCards, knownCards):
        remainingCards = []

        for deckCard in deckCards:
            if deckCard not in knownCards:
                remainingCards.append(deckCard)

        return remainingCards
