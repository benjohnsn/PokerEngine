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


if __name__ == "__main__":
    unittest.main()