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
        for card in cards:
            handVal.append(self.rankValue(card))

        handVal.sort(reverse=True)

        return (0, handVal[0], handVal[1], handVal[2], handVal[3], handVal[4])


    def run(self):
        print("Starting Game...")
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