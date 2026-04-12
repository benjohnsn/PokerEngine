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

    def test_post_blinds(self):
        self.game.postBlinds()

        self.assertEqual(self.p1.stack, 995)
        self.assertEqual(self.p2.stack, 990)
        self.assertEqual(self.p1.currentBet, 5)
        self.assertEqual(self.p2.currentBet, 10)
        self.assertEqual(self.game.pot, 15)

    def test_get_amount_to_call(self):
        self.game.postBlinds()

        amount = self.game.getAmountToCall(self.p1)
        self.assertEqual(amount, 5)

    def test_call(self):
        self.game.postBlinds()

        self.game.call(self.p1)

        self.assertEqual(self.p1.currentBet, 10)
        self.assertEqual(self.p1.stack, 990)
        self.assertEqual(self.game.pot, 20)

    def test_reset_current_bets(self):
        self.game.postBlinds()
        self.game.resetCurrentBets()

        self.assertEqual(self.p1.currentBet, 0)
        self.assertEqual(self.p2.currentBet, 0)

    def test_count_active_players(self):
        self.assertEqual(self.game.countActivePlayers(), 2)

        self.p2.folded = True
        self.assertEqual(self.game.countActivePlayers(), 1)

    def test_hand_fold_win_awards_pot(self):
        self.game.postBlinds()
        self.p2.folded = True

        self.game.handFoldWin()

        self.assertEqual(self.p1.stack, 1010)
        self.assertEqual(self.game.pot, 0)

    def test_showdown_awards_pot(self):
        self.game.postBlinds()

        # p1 stronger (pair of Aces vs Kings)
        self.p1.hand = make_cards(["AS", "AD"])
        self.p2.hand = make_cards(["KS", "KD"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1010)
        self.assertEqual(self.game.pot, 0)

    def test_showdown_split_pot(self):
        self.game.postBlinds()

        # identical hands -> tie
        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["AH", "KC"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1003)
        self.assertEqual(self.p2.stack, 997)
        self.assertEqual(self.game.pot, 0)

    def test_get_highest_bet(self):
        self.game.postBlinds()
        self.assertEqual(self.game.getHighestBet(), 10)

    def test_can_check_when_no_bet_to_call(self):
        self.assertTrue(self.game.canCheck(self.p1))

    def test_cannot_check_when_facing_bet(self):
        self.game.postBlinds()
        self.assertFalse(self.game.canCheck(self.p1))

    def test_can_call_when_player_has_enough_chips(self):
        self.game.postBlinds()
        self.assertTrue(self.game.canCall(self.p1))

    def test_cannot_call_when_player_lacks_chips(self):
        self.game.postBlinds()
        self.p1.stack = 3
        self.assertFalse(self.game.canCall(self.p1))

    def test_is_valid_raise(self):
        self.game.postBlinds()
        self.assertTrue(self.game.isValidRaise(self.p1, 20))

    def test_raise_to_same_as_highest_bet_is_invalid(self):
        self.game.postBlinds()
        self.assertFalse(self.game.isValidRaise(self.p1, 10))

    def test_raise_below_minimum_is_invalid(self):
        self.game.postBlinds()
        self.assertFalse(self.game.isValidRaise(self.p1, 15))

    def test_raise_above_stack_is_invalid(self):
        self.game.postBlinds()
        self.p1.stack = 8
        self.assertFalse(self.game.isValidRaise(self.p1, 20))

    def test_raise_to_updates_stack_bet_and_pot(self):
        self.game.postBlinds()

        self.game.raiseTo(self.p1, 20)

        self.assertEqual(self.p1.stack, 980)
        self.assertEqual(self.p1.currentBet, 20)
        self.assertEqual(self.game.pot, 30)

    def test_invalid_raise_raises_value_error(self):
        self.game.postBlinds()

        with self.assertRaises(ValueError):
            self.game.raiseTo(self.p1, 15)

    def test_invalid_check_raises_value_error(self):
        self.game.postBlinds()

        with self.assertRaises(ValueError):
            self.game.check(self.p1)

    def test_invalid_call_raises_value_error(self):
        self.game.postBlinds()
        self.p1.stack = 3

        with self.assertRaises(ValueError):
            self.game.call(self.p1)

if __name__ == "__main__":
    unittest.main()