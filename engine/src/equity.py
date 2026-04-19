import random

from .deck import Deck
from .evaluator import Evaluator

class EquityCalculator:
    def __init__(self):
        self.evaluator = Evaluator()


    def calculateEquity(self, heroHand, board, numOpponents, simulations):
        if simulations < 1:
            raise ValueError("Simulations must be at least 1.")

        wins = 0
        ties = 0
        losses = 0

        for _ in range(simulations):
            result = self.simulateOnce(heroHand, board, numOpponents)

            if result == "win":
                wins += 1
            elif result == "tie":
                ties += 1
            else:
                losses += 1

        return {
            "winPct": (wins / simulations) * 100,
            "tiePct": (ties / simulations) * 100,
            "lossPct": (losses / simulations) * 100
        }


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
