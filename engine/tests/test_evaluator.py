import unittest
from engine.src.game import Game
from engine.src.evaluator import Evaluator
from engine.src.card import Card


def make_cards(card_strs):
    cards = []
    for card_str in card_strs:
        rank = card_str[:-1]
        suit = card_str[-1]
        cards.append(Card(rank, suit))
    return cards


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.evaluator = Evaluator()

    def test_get_straight_high_regular(self):
        hand_vals = [14, 13, 12, 11, 10, 4, 2]
        self.assertEqual(self.evaluator.getStraightHigh(hand_vals), 14)

    def test_get_straight_high_ace_low(self):
        hand_vals = [14, 5, 4, 3, 2, 9, 8]
        self.assertEqual(self.evaluator.getStraightHigh(hand_vals), 5)

    def test_get_straight_high_none(self):
        hand_vals = [14, 13, 11, 9, 7, 4, 2]
        self.assertEqual(self.evaluator.getStraightHigh(hand_vals), 0)

    def test_high_card(self):
        cards = make_cards(["AS", "KD", "9H", "7C", "4S", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (0, 14, 13, 9, 7, 4))

    def test_one_pair(self):
        cards = make_cards(["AS", "AD", "9H", "7C", "4S", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (1, 14, 9, 7, 4))

    def test_two_pair(self):
        cards = make_cards(["AS", "AD", "KH", "KC", "4S", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (2, 14, 13, 4))

    def test_three_of_a_kind(self):
        cards = make_cards(["AS", "AD", "AH", "KC", "4S", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (3, 14, 13, 4))

    def test_straight(self):
        cards = make_cards(["9S", "8D", "7H", "6C", "5S", "KD", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (4, 9))

    def test_ace_low_straight(self):
        cards = make_cards(["AS", "5D", "4H", "3C", "2S", "KD", "QH"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (4, 5))

    def test_flush(self):
        cards = make_cards(["AS", "JS", "8S", "5S", "2S", "KD", "QH"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (5, 14, 11, 8, 5, 2))

    def test_full_house_from_triple_and_pair(self):
        cards = make_cards(["AS", "AD", "AH", "KC", "KH", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (6, 14, 13))

    def test_full_house_from_two_triples(self):
        cards = make_cards(["AS", "AD", "AH", "KC", "KD", "KH", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (6, 14, 13))

    def test_four_of_a_kind(self):
        cards = make_cards(["AS", "AD", "AH", "AC", "KH", "3D", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (7, 14, 13))

    def test_straight_flush(self):
        cards = make_cards(["9S", "8S", "7S", "6S", "5S", "KD", "2H"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (8, 9))

    def test_ace_low_straight_flush(self):
        cards = make_cards(["AS", "5S", "4S", "3S", "2S", "KD", "QH"])
        score = self.evaluator.evaluateHand(cards)
        self.assertEqual(score, (8, 5))

    def test_higher_pair_beats_lower_pair(self):
        cards1 = make_cards(["AS", "AD", "9H", "7C", "4S", "3D", "2H"])
        cards2 = make_cards(["KS", "KD", "QH", "7C", "4S", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_pair_same_pair_better_kicker_wins(self):
        cards1 = make_cards(["AS", "AD", "KH", "7C", "4S", "3D", "2H"])
        cards2 = make_cards(["AC", "AH", "QH", "7C", "4S", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_higher_two_pair_beats_lower_two_pair(self):
        cards1 = make_cards(["AS", "AD", "KH", "KC", "4S", "3D", "2H"])
        cards2 = make_cards(["QS", "QD", "JH", "JC", "4S", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_two_pair_same_pairs_better_kicker_wins(self):
        cards1 = make_cards(["AS", "AD", "KH", "KC", "QS", "3D", "2H"])
        cards2 = make_cards(["AC", "AH", "KD", "KS", "JS", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_higher_straight_beats_lower_straight(self):
        cards1 = make_cards(["10S", "9D", "8H", "7C", "6S", "2D", "3H"])
        cards2 = make_cards(["9S", "8D", "7H", "6C", "5S", "2D", "3H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_higher_flush_beats_lower_flush(self):
        cards1 = make_cards(["AS", "JS", "8S", "5S", "2S", "KD", "QH"])
        cards2 = make_cards(["KS", "JS", "8S", "5S", "2S", "AD", "QH"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_higher_full_house_beats_lower_full_house(self):
        cards1 = make_cards(["AS", "AD", "AH", "KC", "KH", "3D", "2H"])
        cards2 = make_cards(["KS", "KD", "KH", "QC", "QH", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_quads_better_kicker_wins(self):
        cards1 = make_cards(["AS", "AD", "AH", "AC", "KH", "3D", "2H"])
        cards2 = make_cards(["AS", "AD", "AH", "AC", "QH", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(cards1)
        score2 = self.evaluator.evaluateHand(cards2)
        self.assertGreater(score1, score2)

    def test_straight_flush_beats_four_of_a_kind(self):
        straight_flush = make_cards(["9S", "8S", "7S", "6S", "5S", "KD", "2H"])
        quads = make_cards(["AS", "AD", "AH", "AC", "KH", "3D", "2H"])
        score1 = self.evaluator.evaluateHand(straight_flush)
        score2 = self.evaluator.evaluateHand(quads)
        self.assertGreater(score1, score2)

    def test_format_hand_high_card(self):
        score = (0, 14, 13, 9, 7, 4)
        self.assertEqual(self.evaluator.formatHand(score), "High card: A K 9 7 4")

    def test_format_hand_pair(self):
        score = (1, 14, 9, 7, 4)
        self.assertEqual(self.evaluator.formatHand(score), "Pair: As (9 7 4 kickers)")

    def test_format_hand_straight(self):
        score = (4, 14)
        self.assertEqual(self.evaluator.formatHand(score), "Straight: A K Q J 10")

    def test_format_hand_ace_low_straight(self):
        score = (4, 5)
        self.assertEqual(self.evaluator.formatHand(score), "Straight: 5 4 3 2 A")

    def test_format_hand_full_house(self):
        score = (6, 14, 13)
        self.assertEqual(self.evaluator.formatHand(score), "Full House: As full of Ks")


if __name__ == "__main__":
    unittest.main()