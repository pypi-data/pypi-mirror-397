# Standard
import unittest
from unittest.mock import patch
import io

# Local
import UserResponseCollector.UserQueryReceiver
from BlackjackSim.UserQueryCommandCards import UserQueryCommandCards
from HandsDecksCards.hand import Hand
from HandsDecksCards.card import Card


class Test_UserQueryCommandCards(unittest.TestCase):
    
    def test_cards_command_doCreatePromptText(self):
        receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
        query_preface = 'Enter player deal up to two cards.'
        command = UserQueryCommandCards(receiver, query_preface)
        exp_val = 'Enter player deal up to two cards.\n(examples AS KH QD JC 10S 9H 8D ... 2C): '
        act_val = command._doCreatePromptText()
        self.assertEqual(exp_val, act_val)

    def test_cards_command_doProcessRawResponse(self):
        receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
        command = UserQueryCommandCards(receiver, '')
        exp_val = ('AS KH QD JC 10H 2S', '')
        (card_list, msg) = command._doProcessRawResponse('AS KH QD JC 10H 2S')
        h = Hand()
        h.add_cards(card_list)
        act_val = (str(h), '')
        self.assertTupleEqual(exp_val, act_val)

    def test_cards_command_doProcessRawResponse_bad(self):
        receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
        command = UserQueryCommandCards(receiver, '')
        exp_val = (None, f"\n\'{'AS KH QD JC 10H 2Z'}\' is not a valid list of cards. Please try again.")
        act_val = command._doProcessRawResponse('AS KH QD JC 10H 2Z')
        self.assertTupleEqual(exp_val, act_val)

    def test_cards_command_doValidateProcessedResponse(self):
        receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
        command = UserQueryCommandCards(receiver, '')
        exp_val = (True, '')
        act_val = command._doValidateProcessedResponse([Card('S','Q'), Card('D','2')])
        self.assertTupleEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in first an invalid response, and then a valid response.
    @patch('sys.stdin', io.StringIO('AX\nAS KH QD JC 10H 2S\n'))
    def test_cards_command(self):
        
        receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
        query_preface = 'Enter player deal up to two cards.'
        command = UserQueryCommandCards(receiver, query_preface)
        
        exp_val = 'AS KH QD JC 10H 2S'
        card_list = command.Execute()
        h = Hand()
        h.add_cards(card_list)
        act_val = str(h)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
