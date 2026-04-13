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
        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["QH", "JC"])

        self.p1.contribution = 50
        self.p2.contribution = 50
        self.p1.stack = 950
        self.p2.stack = 950

        self.p2.folded = True
        self.game.pot = 100

        self.game.handFoldWin()

        self.assertEqual(self.p1.stack, 1050)
        self.assertEqual(self.game.pot, 0)


    def test_showdown_awards_pot(self):
        self.p1.hand = make_cards(["AS", "AD"])
        self.p2.hand = make_cards(["KS", "KD"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])

        self.p1.contribution = 50
        self.p2.contribution = 50
        self.p1.stack = 950
        self.p2.stack = 950

        self.fold_other_players([self.p1, self.p2])
        self.game.pot = 100

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1050)
        self.assertEqual(self.p2.stack, 950)
        self.assertEqual(self.game.pot, 0)


    def test_showdown_split_pot(self):
        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["AH", "KC"])
        self.game.board = make_cards(["2H", "3D", "4C", "5S", "9H"])

        self.p1.contribution = 50
        self.p2.contribution = 50
        self.p1.stack = 950
        self.p2.stack = 950

        self.fold_other_players([self.p1, self.p2])
        self.game.pot = 100

        self.game.showdown()

        self.assertEqual(self.p1.stack, 1000)
        self.assertEqual(self.p2.stack, 1000)
        self.assertEqual(self.game.pot, 0)

    def test_should_runout_board_when_only_one_player_can_act(self):
        self.game.newHand()
        self.game.dealHands()

        activePlayers = self.game.getActivePlayers()
        p1 = activePlayers[0]
        p2 = activePlayers[1]

        for player in activePlayers[2:]:
            player.folded = True

        p1.stack = 0
        p2.stack = 100

        self.assertTrue(self.game.shouldRunoutBoard())


    def test_should_not_runout_board_when_two_players_can_act(self):
        self.game.newHand()
        self.game.dealHands()

        activePlayers = self.game.getActivePlayers()
        p1 = activePlayers[0]
        p2 = activePlayers[1]

        for player in activePlayers[2:]:
            player.folded = True

        p1.stack = 100
        p2.stack = 100

        self.assertFalse(self.game.shouldRunoutBoard())


    def test_runout_board_deals_remaining_cards_and_resolves_pot(self):
        self.game.newHand()
        self.game.dealHands()

        activePlayers = self.game.getActivePlayers()
        p1 = activePlayers[0]
        p2 = activePlayers[1]

        for player in activePlayers[2:]:
            player.folded = True

        p1.stack = 0
        p2.stack = 100

        p1.contribution = 50
        p2.contribution = 50
        self.game.pot = 100

        self.game.dealFlop()
        self.assertEqual(len(self.game.board), 3)

        self.assertTrue(self.game.shouldRunoutBoard())

        self.game.runoutBoard()

        self.assertEqual(len(self.game.board), 5)
        self.assertEqual(self.game.pot, 0)

    def test_side_pot_single_side_pot(self):
        self.p1.hand = make_cards(["AS", "AH"])
        self.p2.hand = make_cards(["KS", "KH"])
        self.p3.hand = make_cards(["QS", "QH"])

        self.p1.contribution = 50
        self.p2.contribution = 100
        self.p3.contribution = 100

        self.p1.stack = 0
        self.p2.stack = 0
        self.p3.stack = 0

        self.p4.folded = True
        self.p5.folded = True
        self.p6.folded = True

        self.game.board = make_cards(["2C", "3D", "4H", "5S", "9C"])
        self.game.pot = 250

        self.game.awardPot([])

        self.assertEqual(self.p1.stack, 150)
        self.assertEqual(self.p2.stack, 100)
        self.assertEqual(self.p3.stack, 0)
        self.assertEqual(self.game.pot, 0)

    def test_side_pot_folded_player_cannot_win_side_pot(self):
        self.p1.hand = make_cards(["AS", "AH"])
        self.p2.hand = make_cards(["KS", "KH"])
        self.p3.hand = make_cards(["QS", "QH"])

        self.p1.contribution = 50
        self.p2.contribution = 100
        self.p3.contribution = 100

        self.p1.stack = 0
        self.p2.stack = 0
        self.p3.stack = 0

        self.p3.folded = True
        self.p4.folded = True
        self.p5.folded = True
        self.p6.folded = True

        self.game.board = make_cards(["2C", "3D", "4H", "5S", "9C"])
        self.game.pot = 250

        self.game.awardPot([])

        self.assertEqual(self.p1.stack, 150)
        self.assertEqual(self.p2.stack, 100)
        self.assertEqual(self.p3.stack, 0)
        self.assertEqual(self.game.pot, 0)

    def test_side_pot_tied_main_pot(self):
        self.p1.hand = make_cards(["AS", "KD"])
        self.p2.hand = make_cards(["AH", "KC"])
        self.p3.hand = make_cards(["QS", "QH"])

        self.p1.contribution = 50
        self.p2.contribution = 50
        self.p3.contribution = 100

        self.p1.stack = 0
        self.p2.stack = 0
        self.p3.stack = 0

        self.p4.folded = True
        self.p5.folded = True
        self.p6.folded = True

        self.game.board = make_cards(["2C", "3D", "4H", "5S", "9C"])
        self.game.pot = 200

        self.game.awardPot([])

        self.assertEqual(self.p1.stack, 75)
        self.assertEqual(self.p2.stack, 75)
        self.assertEqual(self.p3.stack, 50)
        self.assertEqual(self.game.pot, 0)

if __name__ == "__main__":
    unittest.main()