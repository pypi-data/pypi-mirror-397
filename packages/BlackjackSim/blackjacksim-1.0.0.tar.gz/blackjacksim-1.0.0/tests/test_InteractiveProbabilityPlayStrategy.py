# Standard
import unittest
import io
from unittest.mock import patch

# Local
from HandsDecksCards.card import Card
from HandsDecksCards.deck import StackedDeck
from BlackjackSim.PlayStrategy import InteractiveProbabilityPlayerPlayStrategy, BlackJackPlayStatus, CasinoDealerPlayStrategy
from BlackjackSim.BlackJackSim import BlackJackSim


class Test_InteractiveProbabilityPlayerPlayStrategy(unittest.TestCase):

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in a stand.
    @patch('sys.stdin', io.StringIO('s\n'))
    def test_stand_on_deal(self):
        # Create the sim object which will provide hand and deck for the play strategy, and play the dealer hand
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create the desired play strategy for the test
        ps = InteractiveProbabilityPlayerPlayStrategy()
       
        # Create a StackedDeck.
        # The first two cards will end up in the player's hand.
        # The third card will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('S','5'), Card('C','2'), Card('C','8')])
        
        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show, bjs)
        
        # Do we have the expected final hand?
        exp_val = '5S 2C'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.STAND
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 7
        act_val = info.Count
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in one hit, then a stand.
    @patch('sys.stdin', io.StringIO('h\ns\n'))
    def test_hit_to_stand(self):
        # Create the sim object which will provide hand and deck for the play strategy, and play the dealer hand
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create the desired play strategy for the test
        ps = InteractiveProbabilityPlayerPlayStrategy()
       
        # Create a StackedDeck.
        # The first two cards will end up in the player's hand.
        # The third card will end up in the dealer's hand, so there is a show card available.
        # The 4th cards will be draw as a hit by the player's hand
        sd = StackedDeck()
        sd.add_cards([Card('S','5'), Card('C','2'), Card('C','8'), Card('D','10')])
        
        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show, bjs)
        
        # Do we have the expected final hand?
        exp_val = '5S 2C 10D'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.STAND
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 17
        act_val = info.Count
        self.assertEqual(exp_val, act_val)
    

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in two hits, which will produce a bust.
    @patch('sys.stdin', io.StringIO('h\nh\n'))
    def test_hit_to_bust(self):
        # Create the sim object which will provide hand and deck for the play strategy, and play the dealer hand
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create the desired play strategy for the test
        ps = InteractiveProbabilityPlayerPlayStrategy()
       
        # Create a StackedDeck.
        # The first two cards will end up in the player's hand.
        # The third card will end up in the dealer's hand, so there is a show card available.
        # The 4th and 5th cards will be draw as hits by the player's hand
        sd = StackedDeck()
        sd.add_cards([Card('S','5'), Card('C','2'), Card('C','8'), Card('D','6'), Card('H','K')])
        
        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show, bjs)
        
        # Do we have the expected final hand?
        exp_val = '5S 2C 6D KH'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.BUST
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 23
        act_val = info.Count
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in True
    @patch('sys.stdin', io.StringIO('y\n'))
    def test_split_yes(self):
        
        ps = InteractiveProbabilityPlayerPlayStrategy()
        
        # Test yes response to splitting query
        exp_val = True
        act_val = ps.split('8', 'K')
        self.assertEqual(exp_val, act_val)
        
    
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in False
    @patch('sys.stdin', io.StringIO('n\n'))
    def test_split_no(self):
        
        ps = InteractiveProbabilityPlayerPlayStrategy()
        
        # Test yes response to splitting query
        exp_val = False
        act_val = ps.split('J', 'K')
        self.assertEqual(exp_val, act_val)
   

if __name__ == '__main__':
    unittest.main()

