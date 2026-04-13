import unittest
from src.game import Game
from src.card import Card
from src.controllers import ScriptedController


def make_cards(card_strs):
    cards = []
    for card_str in card_strs:
        rank = card_str[:-1]
        suit = card_str[-1]
        cards.append(Card(rank, suit))
    return cards


class TestBetting(unittest.TestCase):
    def setUp(self):
        self.game = Game()

        self.p1 = self.game.players[0]
        self.p2 = self.game.players[1]
        self.p3 = self.game.players[2]
        self.p4 = self.game.players[3]
        self.p5 = self.game.players[4]
        self.p6 = self.game.players[5]

    def get_sb(self):
        livePlayers = self.game.getLivePlayers()
        return livePlayers[self.game.getSmallBlindIndex()]

    def get_bb(self):
        livePlayers = self.game.getLivePlayers()
        return livePlayers[self.game.getBigBlindIndex()]

    def deal_hands_to_all_players(self):
        for player in self.game.players:
            player.hand = make_cards(["AS", "KD"])

    def test_get_amount_to_call(self):
        self.game.postBlinds()

        sb = self.get_sb()
        amount = self.game.getAmountToCall(sb)

        self.assertEqual(amount, 5)

    def test_call(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.game.call(sb)

        self.assertEqual(sb.currentBet, 10)
        self.assertEqual(sb.stack, 990)
        self.assertEqual(self.game.pot, 20)

    def test_get_highest_bet(self):
        self.game.postBlinds()
        self.assertEqual(self.game.getHighestBet(), 10)

    def test_can_check_when_no_bet_to_call(self):
        self.assertTrue(self.game.canCheck(self.p1))

    def test_cannot_check_when_facing_bet(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.assertFalse(self.game.canCheck(sb))

    def test_can_call_when_player_has_enough_chips(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.assertTrue(self.game.canCall(sb))

    def test_cannot_call_when_player_lacks_chips(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 0
        self.assertFalse(self.game.canCall(sb))

    def test_is_valid_raise(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.assertTrue(self.game.isValidRaise(sb, 20))

    def test_raise_to_same_as_highest_bet_is_invalid(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.assertFalse(self.game.isValidRaise(sb, 10))

    def test_raise_below_minimum_is_invalid(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.assertFalse(self.game.isValidRaise(sb, 15))

    def test_raise_above_stack_is_invalid(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 8
        self.assertFalse(self.game.isValidRaise(sb, 20))

    def test_raise_to_updates_stack_bet_and_pot(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.game.raiseTo(sb, 20)

        self.assertEqual(sb.stack, 980)
        self.assertEqual(sb.currentBet, 20)
        self.assertEqual(self.game.pot, 30)

    def test_invalid_raise_raises_value_error(self):
        self.game.postBlinds()

        sb = self.get_sb()
        with self.assertRaises(ValueError):
            self.game.raiseTo(sb, 15)

    def test_invalid_check_raises_value_error(self):
        self.game.postBlinds()

        sb = self.get_sb()
        with self.assertRaises(ValueError):
            self.game.check(sb)

    def test_invalid_call_raises_value_error(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 0

        with self.assertRaises(ValueError):
            self.game.call(sb)

    def test_short_stack_can_call_all_in(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 3

        self.assertTrue(self.game.canCall(sb))

    def test_call_uses_remaining_stack_when_player_is_short(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 3

        self.game.call(sb)

        self.assertEqual(sb.stack, 0)
        self.assertEqual(sb.currentBet, 8)
        self.assertEqual(self.game.pot, 18)

    def test_betting_round_complete_when_short_stack_is_all_in(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.hand = make_cards(["AS", "KD"])
        bb = self.get_bb()
        bb.hand = make_cards(["QH", "JC"])

        sb.stack = 3
        self.game.call(sb)

        self.assertTrue(self.game.isBettingRoundComplete())

    def test_all_in_raise_uses_remaining_stack(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.stack = 10

        self.game.raiseTo(sb, 15)

        self.assertEqual(sb.stack, 0)
        self.assertEqual(sb.currentBet, 15)
        self.assertEqual(self.game.pot, 25)

    def test_raise_above_max_bet_is_invalid(self):
        self.game.postBlinds()

        sb = self.get_sb()
        with self.assertRaises(ValueError):
            self.game.raiseTo(sb, 2000)

    def test_valid_raise_updates_correctly(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.game.raiseTo(sb, 20)

        self.assertEqual(sb.currentBet, 20)
        self.assertEqual(sb.stack, 980)
        self.assertEqual(self.game.pot, 30)

    def test_raise_sets_last_raiser(self):
        self.game.postBlinds()

        sb = self.get_sb()
        self.game.raiseTo(sb, 20)

        self.assertEqual(self.game.lastRaiser, sb)

    def test_raise_does_not_complete_round_immediately(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.hand = make_cards(["AS", "KD"])
        bb = self.get_bb()
        bb.hand = make_cards(["QH", "JC"])

        self.game.raiseTo(sb, 20)

        self.assertFalse(self.game.isBettingRoundComplete())

    def test_call_after_raise_completes_round(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.hand = make_cards(["AS", "KD"])
        bb = self.get_bb()
        bb.hand = make_cards(["QH", "JC"])

        self.game.raiseTo(sb, 20)
        self.game.call(bb)

        self.assertTrue(self.game.isBettingRoundComplete())

    def test_multiple_raises_reset_action_cycle(self):
        self.game.postBlinds()

        sb = self.get_sb()
        bb = self.get_bb()

        sb.hand = make_cards(["AS", "KD"])
        bb.hand = make_cards(["QH", "JC"])

        self.game.raiseTo(sb, 20)
        self.game.raiseTo(bb, 40)

        self.assertEqual(self.game.lastRaiser, bb)
        self.assertFalse(self.game.isBettingRoundComplete())

    def test_all_in_does_not_block_round_completion(self):
        self.game.postBlinds()

        sb = self.get_sb()
        sb.hand = make_cards(["AS", "KD"])
        bb = self.get_bb()
        bb.hand = make_cards(["QH", "JC"])

        bb.stack = 5
        self.game.raiseTo(sb, 20)
        self.game.call(bb)

        self.assertTrue(self.game.isBettingRoundComplete())

    def test_preflop_everyone_folds_to_big_blind(self):
        self.deal_hands_to_all_players()
        self.game.postBlinds()

        actingOrder = self.game.getPlayersInOrder(self.game.getUnderTheGunIndex())
        utg = actingOrder[0]
        hj = actingOrder[1]
        co = actingOrder[2]
        button = actingOrder[3]
        sb = actingOrder[4]
        bb = actingOrder[5]

        utg.controller = ScriptedController([("fold", None)])
        hj.controller = ScriptedController([("fold", None)])
        co.controller = ScriptedController([("fold", None)])
        button.controller = ScriptedController([("fold", None)])
        sb.controller = ScriptedController([("fold", None)])
        bb.controller = ScriptedController([])

        self.game.bettingRound(preflop=True)

        self.assertTrue(utg.folded)
        self.assertTrue(hj.folded)
        self.assertTrue(co.folded)
        self.assertTrue(button.folded)
        self.assertTrue(sb.folded)
        self.assertFalse(bb.folded)
        self.assertEqual(self.game.countActivePlayers(), 1)

    def test_preflop_everyone_calls_round_completes(self):
        self.deal_hands_to_all_players()
        self.game.postBlinds()

        actingOrder = self.game.getPlayersInOrder(self.game.getUnderTheGunIndex())
        utg = actingOrder[0]
        hj = actingOrder[1]
        co = actingOrder[2]
        button = actingOrder[3]
        sb = actingOrder[4]
        bb = actingOrder[5]

        utg.controller = ScriptedController([("call", None)])
        hj.controller = ScriptedController([("call", None)])
        co.controller = ScriptedController([("call", None)])
        button.controller = ScriptedController([("call", None)])
        sb.controller = ScriptedController([("call", None)])
        bb.controller = ScriptedController([("check", None)])

        self.game.bettingRound(preflop=True)

        for player in self.game.players:
            self.assertFalse(player.folded)
            self.assertEqual(player.currentBet, 10)

        self.assertEqual(self.game.pot, 60)

    def test_preflop_raise_then_everyone_folds(self):
        self.deal_hands_to_all_players()
        self.game.postBlinds()

        actingOrder = self.game.getPlayersInOrder(self.game.getUnderTheGunIndex())
        utg = actingOrder[0]
        hj = actingOrder[1]
        co = actingOrder[2]
        button = actingOrder[3]
        sb = actingOrder[4]
        bb = actingOrder[5]

        utg.controller = ScriptedController([("raise", 20)])
        hj.controller = ScriptedController([("fold", None)])
        co.controller = ScriptedController([("fold", None)])
        button.controller = ScriptedController([("fold", None)])
        sb.controller = ScriptedController([("fold", None)])
        bb.controller = ScriptedController([("fold", None)])

        self.game.bettingRound(preflop=True)

        self.assertEqual(utg.currentBet, 20)
        self.assertTrue(hj.folded)
        self.assertTrue(co.folded)
        self.assertTrue(button.folded)
        self.assertTrue(sb.folded)
        self.assertTrue(bb.folded)
        self.assertEqual(self.game.countActivePlayers(), 1)
        self.assertEqual(self.game.lastRaiser, utg)

    def test_preflop_raise_then_big_blind_calls(self):
        self.deal_hands_to_all_players()
        self.game.postBlinds()

        actingOrder = self.game.getPlayersInOrder(self.game.getUnderTheGunIndex())
        utg = actingOrder[0]
        hj = actingOrder[1]
        co = actingOrder[2]
        button = actingOrder[3]
        sb = actingOrder[4]
        bb = actingOrder[5]

        utg.controller = ScriptedController([("raise", 20)])
        hj.controller = ScriptedController([("fold", None)])
        co.controller = ScriptedController([("fold", None)])
        button.controller = ScriptedController([("fold", None)])
        sb.controller = ScriptedController([("fold", None)])
        bb.controller = ScriptedController([("call", None)])

        self.game.bettingRound(preflop=True)

        self.assertEqual(utg.currentBet, 20)
        self.assertEqual(bb.currentBet, 20)
        self.assertFalse(utg.folded)
        self.assertFalse(bb.folded)
        self.assertEqual(self.game.countActivePlayers(), 2)
        self.assertEqual(self.game.pot, 45)

    def test_postflop_everyone_checks(self):
        self.deal_hands_to_all_players()

        for player in self.game.players:
            player.controller = ScriptedController([("check", None)])

        self.game.bettingRound(preflop=False)

        for player in self.game.players:
            self.assertFalse(player.folded)
            self.assertEqual(player.currentBet, 0)

        self.assertEqual(self.game.pot, 0)

    def test_postflop_bet_then_all_fold(self):
        self.deal_hands_to_all_players()

        actingOrder = self.game.getPlayersInOrder(
            (self.game.dealerIndex + 1) % len(self.game.getLivePlayers())
        )
        firstToAct = actingOrder[0]
        secondToAct = actingOrder[1]
        thirdToAct = actingOrder[2]
        fourthToAct = actingOrder[3]
        fifthToAct = actingOrder[4]
        sixthToAct = actingOrder[5]

        firstToAct.controller = ScriptedController([("raise", 10)])
        secondToAct.controller = ScriptedController([("fold", None)])
        thirdToAct.controller = ScriptedController([("fold", None)])
        fourthToAct.controller = ScriptedController([("fold", None)])
        fifthToAct.controller = ScriptedController([("fold", None)])
        sixthToAct.controller = ScriptedController([("fold", None)])

        self.game.bettingRound(preflop=False)

        self.assertEqual(firstToAct.currentBet, 10)
        self.assertFalse(firstToAct.folded)
        self.assertTrue(secondToAct.folded)
        self.assertTrue(thirdToAct.folded)
        self.assertTrue(fourthToAct.folded)
        self.assertTrue(fifthToAct.folded)
        self.assertTrue(sixthToAct.folded)
        self.assertEqual(self.game.countActivePlayers(), 1)
        self.assertEqual(self.game.pot, 10)

    def test_postflop_bet_and_call(self):
        self.deal_hands_to_all_players()

        actingOrder = self.game.getPlayersInOrder(
            (self.game.dealerIndex + 1) % len(self.game.getLivePlayers())
        )
        firstToAct = actingOrder[0]
        secondToAct = actingOrder[1]
        thirdToAct = actingOrder[2]
        fourthToAct = actingOrder[3]
        fifthToAct = actingOrder[4]
        sixthToAct = actingOrder[5]

        firstToAct.controller = ScriptedController([("raise", 10)])
        secondToAct.controller = ScriptedController([("call", None)])
        thirdToAct.controller = ScriptedController([("fold", None)])
        fourthToAct.controller = ScriptedController([("fold", None)])
        fifthToAct.controller = ScriptedController([("fold", None)])
        sixthToAct.controller = ScriptedController([("fold", None)])

        self.game.bettingRound(preflop=False)

        self.assertEqual(firstToAct.currentBet, 10)
        self.assertEqual(secondToAct.currentBet, 10)
        self.assertFalse(firstToAct.folded)
        self.assertFalse(secondToAct.folded)
        self.assertEqual(self.game.countActivePlayers(), 2)
        self.assertEqual(self.game.pot, 20)

    def test_postflop_raise_reraise_call(self):
        self.deal_hands_to_all_players()

        actingOrder = self.game.getPlayersInOrder(
            (self.game.dealerIndex + 1) % len(self.game.getLivePlayers())
        )
        firstToAct = actingOrder[0]
        secondToAct = actingOrder[1]
        thirdToAct = actingOrder[2]
        fourthToAct = actingOrder[3]
        fifthToAct = actingOrder[4]
        sixthToAct = actingOrder[5]

        firstToAct.controller = ScriptedController([("raise", 10), ("call", None)])
        secondToAct.controller = ScriptedController([("raise", 20)])
        thirdToAct.controller = ScriptedController([("fold", None)])
        fourthToAct.controller = ScriptedController([("fold", None)])
        fifthToAct.controller = ScriptedController([("fold", None)])
        sixthToAct.controller = ScriptedController([("fold", None)])

        self.game.bettingRound(preflop=False)

        self.assertEqual(firstToAct.currentBet, 20)
        self.assertEqual(secondToAct.currentBet, 20)
        self.assertFalse(firstToAct.folded)
        self.assertFalse(secondToAct.folded)
        self.assertEqual(self.game.lastRaiser, secondToAct)
        self.assertEqual(self.game.pot, 40)

    def test_postflop_short_stack_all_in_call_does_not_block_completion(self):
        self.deal_hands_to_all_players()

        actingOrder = self.game.getPlayersInOrder(
            (self.game.dealerIndex + 1) % len(self.game.getLivePlayers())
        )
        firstToAct = actingOrder[0]
        secondToAct = actingOrder[1]
        thirdToAct = actingOrder[2]
        fourthToAct = actingOrder[3]
        fifthToAct = actingOrder[4]
        sixthToAct = actingOrder[5]

        secondToAct.stack = 5

        firstToAct.controller = ScriptedController([("raise", 10)])
        secondToAct.controller = ScriptedController([("call", None)])
        thirdToAct.controller = ScriptedController([("fold", None)])
        fourthToAct.controller = ScriptedController([("fold", None)])
        fifthToAct.controller = ScriptedController([("fold", None)])
        sixthToAct.controller = ScriptedController([("fold", None)])

        self.game.bettingRound(preflop=False)

        self.assertEqual(secondToAct.stack, 0)
        self.assertEqual(secondToAct.currentBet, 5)
        self.assertEqual(firstToAct.currentBet, 10)
        self.assertEqual(self.game.pot, 15)


if __name__ == "__main__":
    unittest.main()