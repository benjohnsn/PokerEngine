from .deck import Deck
from .player import Player
from .constants import VALUE_TO_RANK

class Game:
    def __init__(self):
        self.players = [Player("Hero"), Player("Villain")]
        self.deck = Deck()
        self.board = []
        self.pot = 0


    def run(self):
        self.newHand()
        self.deck.shuffle()
        self.postBlinds()

        self.dealHands()
        self.bettingRound()
        self.resetCurrentBets()

        self.burn()
        self.dealFlop()
        self.bettingRound()
        self.resetCurrentBets()

        self.burn()
        self.dealTurn()
        self.bettingRound()
        self.resetCurrentBets()

        self.burn()
        self.dealRiver()
        self.bettingRound()
        self.resetCurrentBets()

        self.showState()
        self.showdown()


    def newHand(self):
        self.board = []
        self.deck = Deck()
        self.pot = 0
        for player in self.players:
            player.newHand()


    def postBlinds(self):
        smallBlind = 5
        bigBlind = 10

        sbPlayer = self.players[0]
        bbPlayer = self.players[1]

        sbPlayer.stack -= smallBlind
        sbPlayer.currentBet = smallBlind

        bbPlayer.stack -= bigBlind
        bbPlayer.currentBet = bigBlind

        self.pot += smallBlind + bigBlind


    def getAmountToCall(self, player):
        highestBet = 0

        for otherPlayer in self.players:
            if otherPlayer.currentBet > highestBet:
                highestBet = otherPlayer.currentBet

        return highestBet - player.currentBet


    def call(self, player):
        amountToCall = self.getAmountToCall(player)
        player.stack -= amountToCall
        player.currentBet += amountToCall
        self.pot += amountToCall


    def check(self, player):
        pass


    def fold(self, player):
        player.folded = True


    def bettingRound(self):
        for player in self.players:
            if player.folded:
                continue
            amountToCall = self.getAmountToCall(player)
            if amountToCall == 0:
                self.check(player)
                print(player.name, "checks")
            else:
                self.call(player)
                print(player.name, "calls", amountToCall)


    def resetCurrentBets(self):
        for player in self.players:
            player.currentBet = 0


    def dealHands(self):
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())


    def burn(self):
        self.deck.deal()


    def dealFlop(self):
        for _ in range(3):
            self.board.append(self.deck.deal())


    def dealTurn(self):
        self.board.append(self.deck.deal())


    def dealRiver(self):
        self.board.append(self.deck.deal())


    def showState(self):
        for player in self.players:
            print(player.name, player.hand, "Stack:", player.stack, "Bet:", player.currentBet)
        print("Board:", self.board)
        print("Pot:", self.pot)


    def showdown(self):
        p1Score = self.evaluateHand(self.players[0].hand + self.board)
        p2Score = self.evaluateHand(self.players[1].hand + self.board)

        if p1Score > p2Score:
            print(self.players[0], "wins with", self.formatHand(p1Score))
        elif p2Score > p1Score:
            print(self.players[1], "wins with", self.formatHand(p2Score))
        else:
            print("Tie!", self.formatHand(p1Score))


    def evaluateHand(self, cards):
        handVals = []
        valueCounts = {}
        suits = {"S": [], "H": [], "D": [], "C": []}
        flushVals = []

        for card in cards:
            handVals.append(card.value)
            suits[card.suit].append(card.value)
        handVals.sort(reverse=True)

        straightFlushHighVal = 0
        for flushSuit in suits:
            if len(suits[flushSuit]) >= 5:
                straightFlushHighVal = self.getStraightHigh(suits[flushSuit])
                break

        straightHighVal = self.getStraightHigh(handVals)

        for val in handVals:
            if val in valueCounts:
                valueCounts[val] += 1
            else:
                valueCounts[val] = 1

        for flushSuit in suits:
            if len(suits[flushSuit]) >= 5:
                suits[flushSuit].sort(reverse=True)
                for i in range(5):
                    flushVals.append(suits[flushSuit][i])
                break

        quadVal = 0
        for val in valueCounts:
            if valueCounts[val] == 4:
                quadVal = val

        tripleVals = []
        for val in valueCounts:
            if valueCounts[val] == 3:
                tripleVals.append(val)
        tripleVals.sort(reverse=True)

        pairVals = []
        for val in valueCounts:
            if valueCounts[val] == 2:
                pairVals.append(val)
        pairVals.sort(reverse=True)

        if straightFlushHighVal:
            return (8, straightFlushHighVal)

        elif quadVal:
            kicker = 0
            for val in handVals:
                if val != quadVal:
                    kicker = val
                    break
            return (7, quadVal, kicker)

        elif len(tripleVals) >= 1 and (len(pairVals) >= 1 or len(tripleVals) >= 2):
            if len(pairVals) >= 1:
                return (6, tripleVals[0], pairVals[0])
            else:
                return (6, tripleVals[0], tripleVals[1])

        elif flushVals:
            return (5, flushVals[0], flushVals[1], flushVals[2], flushVals[3], flushVals[4])

        elif straightHighVal:
            return (4, straightHighVal)

        elif len(tripleVals) >= 1:
            kickers = []
            for val in handVals:
                if len(kickers) == 2:
                    break
                if val != tripleVals[0]:
                    kickers.append(val)
            return (3, tripleVals[0], kickers[0], kickers[1])

        elif len(pairVals) >= 2:
            highPair = pairVals[0]
            lowPair = pairVals[1]
            for val in handVals:
                if val != highPair and val != lowPair:
                    kicker = val
                    break
            return (2, highPair, lowPair, kicker)

        elif len(pairVals) == 1:
            kickers = []
            for val in handVals:
                if len(kickers) == 3:
                    break
                if val != pairVals[0]:
                    kickers.append(val)
            return (1, pairVals[0], kickers[0], kickers[1], kickers[2])

        else:
            return (0, handVals[0], handVals[1], handVals[2], handVals[3], handVals[4])


    def getStraightHigh(self, handVals):
        aceLowStraight = {14, 2, 3, 4, 5}

        straightSet = set(handVals)
        straightVals = list(straightSet)
        straightVals.sort(reverse=True)
        straightHighVal = 0
        run = 1

        for i in range(len(straightVals) - 1):
            if straightVals[i] == straightVals[i+1] + 1:
                run += 1
            else:
                run = 1
            if run == 5:
                straightHighVal = straightVals[i-3]
                break

        if straightHighVal == 0:
            if aceLowStraight.issubset(straightSet):
                straightHighVal = 5

        return straightHighVal


    def formatHand(self, score):
        handType = score[0]

        if handType == 8:
            straightFlushHighVal = score[1]
            if straightFlushHighVal == 5:
                return f"Straight Flush: 5 4 3 2 A"
            v1 = VALUE_TO_RANK[straightFlushHighVal]
            v2 = VALUE_TO_RANK[straightFlushHighVal - 1]
            v3 = VALUE_TO_RANK[straightFlushHighVal - 2]
            v4 = VALUE_TO_RANK[straightFlushHighVal - 3]
            v5 = VALUE_TO_RANK[straightFlushHighVal - 4]
            return f"Straight Flush: {v1} {v2} {v3} {v4} {v5}"

        elif handType == 7:
            quad = VALUE_TO_RANK[score[1]]
            kicker = VALUE_TO_RANK[score[2]]
            return f"Four of a kind: {quad}s ({kicker} kicker)"

        elif handType == 6:
            triple = VALUE_TO_RANK[score[1]]
            pair = VALUE_TO_RANK[score[2]]
            return f"Full House: {triple}s full of {pair}s"

        elif handType == 5:
            v1 = VALUE_TO_RANK[score[1]]
            v2 = VALUE_TO_RANK[score[2]]
            v3 = VALUE_TO_RANK[score[3]]
            v4 = VALUE_TO_RANK[score[4]]
            v5 = VALUE_TO_RANK[score[5]]
            return f"Flush: {v1} {v2} {v3} {v4} {v5}"

        elif handType == 4:
            straightHighVal = score[1]
            if straightHighVal == 5:
                return f"Straight: 5 4 3 2 A"
            v1 = VALUE_TO_RANK[straightHighVal]
            v2 = VALUE_TO_RANK[straightHighVal - 1]
            v3 = VALUE_TO_RANK[straightHighVal - 2]
            v4 = VALUE_TO_RANK[straightHighVal - 3]
            v5 = VALUE_TO_RANK[straightHighVal - 4]
            return f"Straight: {v1} {v2} {v3} {v4} {v5}"

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
