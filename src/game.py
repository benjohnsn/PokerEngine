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

        player1Cards = self.player1Hand + self.board
        bestValue = self.rankValue(player1Cards[0])
        bestCard = player1Cards[0]

        for card in player1Cards:
            newValue = self.rankValue(card)
            if newValue > bestValue:
                bestValue = newValue
                bestCard = card

        player1Max = bestValue
        player1HighCard = bestCard

        player2Cards = self.player2Hand + self.board
        bestValue = self.rankValue(player2Cards[0])
        bestCard = player2Cards[0]

        for card in player2Cards:
            newValue = self.rankValue(card)
            if newValue > bestValue:
                bestValue = newValue
                bestCard = card

        player2Max = bestValue
        player2HighCard = bestCard

        if player1Max > player2Max:
            print(self.players[0], "wins with", player1HighCard)
        elif player1Max < player2Max:
            print(self.players[1], "wins with", player2HighCard)
        else:
            print("Tie! (high card:", player1HighCard, ")")