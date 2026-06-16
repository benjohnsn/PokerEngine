class TightAggressiveController:
    def getAction(self, game, player, validActions, amountToCall):
        if len(game.board) == 0:
            return self.getPreflopAction(game, player, validActions, amountToCall)
        else:
            return self.getPostflopAction(game, player, validActions, amountToCall)


    def getPreflopAction(self, game, player, validActions, amountToCall):
        handCategory = self.classifyPreflopHand(player.hand)

        if handCategory == "premium":
            # Strong hands should be played aggressively, but not escalate forever
            if "raise" in validActions:
                if amountToCall == 0:
                    # No pressure → open the pot
                    targetBet = 10
                    if game.isValidRaise(player, targetBet):
                        return "raise", targetBet

                elif amountToCall <= 10:
                    # Facing a small raise → re-raise for value
                    targetBet = game.getHighestBet() * 3
                    if game.isValidRaise(player, targetBet):
                        return "raise", targetBet

            # Facing larger aggression → continue but avoid over-escalating
            if "call" in validActions:
                return "call", None
            if "check" in validActions:
                return "check", None

        elif handCategory == "playable":
            # Decent hands: can open when checked to, otherwise play cautiously
            if amountToCall == 0 and "raise" in validActions:
                # Opportunity to take initiative
                targetBet = 10
                if game.isValidRaise(player, targetBet):
                    return "raise", targetBet

            if "call" in validActions and amountToCall <= 10:
                # Cheap enough to continue
                return "call", None

            if "check" in validActions:
                return "check", None

            if "fold" in validActions:
                return "fold", None

        else:
            # Weak hands: avoid putting money in unless free
            if "check" in validActions:
                return "check", None

            if "fold" in validActions:
                return "fold", None

        raise ValueError("No valid action found")


    def getPostflopAction(self, game, player, validActions, amountToCall):
        strength = self.classifyPostflopHand(game, player)

        if strength == "strong":
            if "raise" in validActions:
                targetBet = game.getHighestBet() + max(10, game.pot // 2)
                if game.isValidRaise(player, targetBet):
                    return "raise", targetBet
            if "call" in validActions:
                return "call", None
            if "check" in validActions:
                return "check", None
            
        elif strength == "medium":
            if "call" in validActions and amountToCall <= max(10, game.pot // 4):
                return "call", None
            if "check" in validActions:
                return "check", None
            if "fold" in validActions:
                return "fold", None

        else:
            if "check" in validActions:
                return "check", None
            if "fold" in validActions:
                return "fold", None

        raise ValueError("No valid postflop action found")


    def classifyPreflopHand(self, hand):
        card1 = hand[0]
        card2 = hand[1]
        v1 = card1.value
        v2 = card2.value

        highVal = max(v1, v2)
        lowVal = min(v1, v2)
        isPair = v1 == v2
        isSuited = card1.suit == card2.suit

        # Premium: JJ+, AK
        if isPair and highVal >= 11:
            return "premium"

        if {v1, v2} == {14, 13}:
            return "premium"

        # Playable: 88-TT
        if isPair and highVal >= 8:
            return "playable"

        # Playable broadways: AQ, AJ, KQ, KJ, QJ
        if {v1, v2} in ({14, 12}, {14, 11}, {13, 12}, {13, 11}, {12, 11}):
            return "playable"

        # Playable suited broadways: KTs+, QTs+, JTs
        if isSuited and highVal >= 11 and lowVal >= 10:
            return "playable"

        # Playable suited connectors: T9s, 98s, 87s
        if isSuited and highVal - lowVal == 1 and highVal >= 9:
            return "playable"

        return "trash"


    def classifyPostflopHand(self, game, player):
        cards = player.hand + game.board
        score = game.evaluator.evaluateHand(cards)
        handType = score[0]

        # Strong made hands
        if handType >= 2:  # two pair or better
            return "strong"

        # One pair logic
        if handType == 1:
            pairVal = score[1]
            holeVals = [card.value for card in player.hand]
            boardVals = [card.value for card in game.board]

            # Overpair: pocket pair higher than any board card
            if player.hand[0].value == player.hand[1].value:
                if pairVal == player.hand[0].value and pairVal > max(boardVals):
                    return "strong"

            # Top pair
            if pairVal == max(boardVals):
                return "medium"

            # Any other pair
            return "medium"

        # Draw logic for high card hands
        if self.hasFlushDraw(cards):
            return "medium"

        if self.hasOpenEndedStraightDraw(cards):
            return "medium"

        return "weak"


    def hasFlushDraw(self, cards):
        suitCounts = {}

        for card in cards:
            if card.suit in suitCounts:
                suitCounts[card.suit] += 1
            else:
                suitCounts[card.suit] = 1

        for suit in suitCounts:
            if suitCounts[suit] == 4:
                return True

        return False


    def hasOpenEndedStraightDraw(self, cards):
        values = sorted(set(card.value for card in cards))

        # Add wheel support: A can also act as 1
        if 14 in values:
            values.append(1)
            values.sort()

        for i in range(len(values) - 3):
            window = values[i:i + 4]

            if window[3] - window[0] == 3:
                consecutive = True
                for j in range(3):
                    if window[j + 1] != window[j] + 1:
                        consecutive = False
                        break
                if consecutive:
                    return True

        return False