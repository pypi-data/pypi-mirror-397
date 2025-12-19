# Standard
import unittest

# Local
from BlackjackSim.BlackJackSim import BlackJackSim
from BlackjackSim.PlayStrategy import BlackJackPlayStatus, ProbabilityPlayerPlayStrategy, CasinoDealerPlayStrategy
from HandsDecksCards.deck import StackedDeck
from HandsDecksCards.card import Card

class Test_ProbabilityPlayerPlayStrategy(unittest.TestCase):
    
    def test_play_stand(self):
        
        # Create the sim object which will provide hand and deck for the play strategy, and play the dealer hand
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create the desired play strategy for the test
        ps = ProbabilityPlayerPlayStrategy()
       
        # Create a StackedDeck.
        # The first two cards will end up in the player's hand.
        # The third card will end up in the dealer's hand, so there is a show card available.
        # The rest don't matter as there should be no draws during play.
        sd = StackedDeck()
        sd.add_cards([Card('C','10'), Card('S','8'), Card('D','5'), Card('H','2')])
        
        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show, bjs)
        
        # Do we have the expected final hand?
        exp_val = '10C 8S'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.STAND
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 18
        act_val = info.Count
        self.assertEqual(exp_val, act_val)


    def test_play_hit(self):
        
        # Create the sim object which will provide hand and deck for the play strategy, and play the dealer hand
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create the desired play strategy for the test
        ps = ProbabilityPlayerPlayStrategy()
       
        # Create a StackedDeck.
        # The first two cards (deal), and the fourth card (hit) will end up in the player's hand.
        # The third card will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('S','5'), Card('D','5'), Card('C','5')])
        
        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show, bjs)
        
        # Do we have the expected final hand?
        exp_val = 'AC 5S 5C'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.STAND
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 21
        act_val = info.Count
        self.assertEqual(exp_val, act_val)


    def test_split(self):
        ps = ProbabilityPlayerPlayStrategy()
        exp_val = False
        act_val = ps.split()
        self.assertEqual(exp_val, act_val)
                        
                
if __name__ == '__main__':
    unittest.main()

