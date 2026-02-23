from .deck import Deck

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


    def rankValue(self, card):
        values = {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
            "7": 7, "8": 8, "9": 9, "10": 10,
            "J": 11, "Q": 12, "K": 13, "A": 14
        }
        return values[card.rank]
    

    def evaluateHand(self, cards):
        handVal = []
        counts = {}

        for card in cards:
            handVal.append(self.rankValue(card))
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


    def run(self):
        self.newHand()

        print("Players:", self.players)

        self.deck.shuffle()
        self.dealHands()

        for _ in range(3):
            self.board.append(self.deck.deal())
        self.board.append(self.deck.deal())
        self.board.append(self.deck.deal())

        print(self.player1Hand)
        print(self.player2Hand)
        print(self.board)

        p1Score = self.evaluateHand(self.player1Hand + self.board)
        p2Score = self.evaluateHand(self.player2Hand + self.board)

        if p1Score > p2Score:
            print(self.players[0], "wins with", p1Score)
        elif p2Score > p1Score:
            print(self.players[1], "wins with", p2Score)
        else:
            print("Tie!", p1Score)
        
    def newHand(self):
        self.player1Hand = []
        self.player2Hand = []
        self.board = []
        self.deck = Deck()