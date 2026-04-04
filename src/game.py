from .deck import Deck
from .constants import VALUE_TO_RANK

class Game:
    def __init__(self):
        self.players = ["Player 1", "Player 2"]
        self.deck = Deck()
        self.player1Hand = []
        self.player2Hand = []
        self.board = []


    def dealHands(self):
        self.player1Hand.append(self.deck.deal())
        self.player1Hand.append(self.deck.deal())
        self.player2Hand.append(self.deck.deal())
        self.player2Hand.append(self.deck.deal())


    def evaluateHand(self, cards):
        handVal = []
        counts = {}

        for card in cards:
            handVal.append(card.value)
        handVal.sort(reverse=True)

        for val in handVal:
            if val in counts:
                counts[val] += 1
            else:
                counts[val] = 1

        quadVal = 0
        for val in counts:
            if counts[val] == 4:
                quadVal = val

        tripleVals = []
        for val in counts:
            if counts[val] == 3:
                tripleVals.append(val)
        tripleVals.sort(reverse=True)

        pairVals = []
        for val in counts:
            if counts[val] == 2:
                pairVals.append(val)
        pairVals.sort(reverse=True)

        if quadVal:
            kicker = 0
            for val in handVal:
                if val != quadVal:
                    kicker = val
                    break
            return (7, quadVal, kicker)
        elif len(tripleVals) >= 1 and (len(pairVals) >= 1 or len(tripleVals) >= 2):
            if len(pairVals) >= 1:
                return (6, tripleVals[0], pairVals[0])
            else:
                return (6, tripleVals[0], tripleVals[1])
        elif len(tripleVals) >= 1:
            kickers = []
            for val in handVal:
                if len(kickers) == 2:
                    break
                if val != tripleVals[0]:
                    kickers.append(val)
            return (3, tripleVals[0], kickers[0], kickers[1])
        elif len(pairVals) >= 2:
            highPair = pairVals[0]
            lowPair = pairVals[1]
            for val in handVal:
                if val != highPair and val != lowPair:
                    kicker = val
                    break
            return (2, highPair, lowPair, kicker)
        elif len(pairVals) == 1:
            kickers = []
            for val in handVal:
                if len(kickers) == 3:
                    break
                if val != pairVals[0]:
                    kickers.append(val)
            return (1, pairVals[0], kickers[0], kickers[1], kickers[2])
        else:
            return (0, handVal[0], handVal[1], handVal[2], handVal[3], handVal[4])


    def formatHand(self, score):
        handType = score[0]

        if handType == 7:
            quad = VALUE_TO_RANK[score[1]]
            kicker = VALUE_TO_RANK[score[2]]
            return f"Four of a kind: {quad}s ({kicker} kicker)"
        elif handType == 6:
            triple = VALUE_TO_RANK[score[1]]
            pair = VALUE_TO_RANK[score[2]]
            return f"Full House: {triple}s full of {pair}s"
        elif handType == 3:
            triple = VALUE_TO_RANK[score[1]]
            k1 = VALUE_TO_RANK[score[2]]
            k2 = VALUE_TO_RANK[score[3]]
            return f"Three of a kind: {triple}s ({k1} {k2} kickers)"
        elif handType == 2:
            highPair = VALUE_TO_RANK[score[1]]
            lowPair = VALUE_TO_RANK[score[2]]
            kicker = VALUE_TO_RANK[score[3]]
            return f"Two pair: {highPair}s and {lowPair}s ({kicker} kicker)"
        elif handType == 1:
            pair = VALUE_TO_RANK[score[1]]
            k1 = VALUE_TO_RANK[score[2]]
            k2 = VALUE_TO_RANK[score[3]]
            k3 = VALUE_TO_RANK[score[4]]
            return f"Pair: {pair}s ({k1} {k2} {k3} kickers)"
        elif handType == 0:
            v1 = VALUE_TO_RANK[score[1]]
            v2 = VALUE_TO_RANK[score[2]]
            v3 = VALUE_TO_RANK[score[3]]
            v4 = VALUE_TO_RANK[score[4]]
            v5 = VALUE_TO_RANK[score[5]]
            return f"High card: {v1} {v2} {v3} {v4} {v5}"


    def run(self):
        self.newHand()

        print("Players:", self.players)

        self.deck.shuffle()
        self.dealHands()

        self.dealFlop()
        self.dealTurn()
        self.dealRiver()

        self.showState()

        p1Score = self.evaluateHand(self.player1Hand + self.board)
        p2Score = self.evaluateHand(self.player2Hand + self.board)

        if p1Score > p2Score:
            print(self.players[0], "wins with", self.formatHand(p1Score))
        elif p2Score > p1Score:
            print(self.players[1], "wins with", self.formatHand(p2Score))
        else:
            print("Tie!", self.formatHand(p1Score))


    def dealFlop(self):
        for _ in range(3):
            self.board.append(self.deck.deal())


    def dealTurn(self):
        self.board.append(self.deck.deal())


    def dealRiver(self):
        self.board.append(self.deck.deal())


    def showState(self):
        print(self.player1Hand)
        print(self.player2Hand)
        print(self.board)

    
    def newHand(self):
        self.player1Hand = []
        self.player2Hand = []
        self.board = []
        self.deck = Deck()