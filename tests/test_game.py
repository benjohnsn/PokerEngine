import unittest
from src.game import Game
from src.card import Card


def make_cards(card_strs):
    cards = []
    for card_str in card_strs:
        rank = card_str[:-1]
        suit = card_str[-1]
        cards.append(Card(rank, suit))
    return cards


class TestGame(unittest.TestCase):
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

    def fold_other_players(self, keep_players):
        for player in self.game.players:
            if player not in keep_players:
                player.folded = True

    def test_post_blinds(self):
        self.game.postBlinds()

        sb = self.get_sb()
        bb = self.get_bb()

        self.assertEqual(sb.stack, 995)
        self.assertEqual(bb.stack, 990)
        self.assertEqual(sb.currentBet, 5)
        self.assertEqual(bb.currentBet, 10)
        self.assertEqual(self.game.pot, 15)

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

    def test_reset_current_bets(self):
        self.game.postBlinds()
        self.game.resetCurrentBets()

        for player in self.game.players:
            self.assertEqual(player.currentBet, 0)

    def test_count_active_players(self):
        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["QH", "JC"])

        self.assertEqual(self.game.countActivePlayers(), 2)

        self.p2.folded = True
        self.assertEqual(self.game.countActivePlayers(), 1)

    def test_hand_fold_win_awards_pot(self):
        self.game.postBlinds()

        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["QH", "JC"])
        self.p2.folded = True

        self.game.handFoldWin()

        self.assertEqual(self.p1.stack, 1015)
        self.assertEqual(self.game.pot, 0)

    def test_showdown_awards_pot(self):
        self.game.postBlinds()

        self.p1.hand = make_cards(["AS", "AD"])
        self.p2.hand = make_cards(["KS", "KD"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])
        self.fold_other_players([self.p1, self.p2])

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1015)
        self.assertEqual(self.game.pot, 0)

    def test_showdown_split_pot(self):
        self.game.postBlinds()

        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["AH", "KC"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])
        self.fold_other_players([self.p1, self.p2])

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1008)
        self.assertEqual(self.p2.stack, 1002)
        self.assertEqual(self.game.pot, 0)

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


if __name__ == "__main__":
    unittest.main()