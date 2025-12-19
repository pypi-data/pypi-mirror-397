# Standard
import unittest

# Local
from BlackjackSim.BlackJackSim import BlackJackSim
from BlackjackSim.PlayStrategy import BlackJackPlayStatus, CasinoDealerPlayStrategy
from HandsDecksCards.hand import Hand
from HandsDecksCards.deck import StackedDeck
from HandsDecksCards.card import Card

class Test_CasinoDealerPlayStrategy(unittest.TestCase):
    
    def test_split(self):
        ps = CasinoDealerPlayStrategy()
        exp_val = False
        act_val = ps.split()
        self.assertEqual(exp_val, act_val)
        
    
    def test_play_stand_min(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('C','8'), Card('D','J'), Card('S','5'), Card('H','2')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
        
        # Do we have the expected final hand?
        exp_val = '8C JD'
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


    def test_play_stand_max(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','5'), Card('H','2')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
                
        # Do we have the expected final hand?
        exp_val = 'AC JD'
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
       
    
    def test_play_hit_to_stand_max(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2, 4 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('S','5'), Card('H','2'), Card('D','J'), Card('C','A')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
                
        # Do we have the expected final hand?
        exp_val = '5S 2H AC'
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

   
    def test_play_hit_to_bust_max_stand_min(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2, 4 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('S','7'), Card('H','9'), Card('D','J'), Card('C','A')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
        
        # Do we have the expected final hand?
        exp_val = '7S 9H AC'
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
        

    def test_play_hit_to_bust_max_hit_to_stand_min(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2, 4, 5 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('S','7'), Card('H','8'), Card('D','J'), Card('C','A'), Card('D','3')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
        
        # Do we have the expected final hand?
        exp_val = '7S 8H AC 3D'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.STAND
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 19
        act_val = info.Count
        self.assertEqual(exp_val, act_val)
        
    
    def test_play_hit_to_bust_max_hit_to_bust_min(self):
        
        # Create the sim object which will provide hand and deck for the play strategy
        bjs = BlackJackSim()
                
        ps = CasinoDealerPlayStrategy()
        
        # Create a StackedDeck.
        # Card 1, 2, 4, 5 will end up in the player's hand.
        # Card 3 will end up in the dealer's hand, so there is a show card available.
        sd = StackedDeck()
        sd.add_cards([Card('S','7'), Card('H','8'), Card('D','J'), Card('C','A'), Card('D','J')])

        # Assign the created deck to the sim object
        bjs.switch_deck(sd)
        
        # Add cards to the player's hand in the sim
        bjs.draw_for_player(2)
        
        # Add show card to dealer's hand in the sim
        bjs.draw_for_dealer(1)
        
        # Play the hand
        info = ps.play(bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)        
        
        # Do we have the expected final hand?
        exp_val = '7S 8H AC JD'
        act_val = info.Final_Hand
        self.assertEqual(exp_val, act_val)
        # Do we have the expected status?
        exp_val = BlackJackPlayStatus.BUST
        act_val = info.Status
        self.assertEqual(exp_val, act_val)
        # Do we have the expected final count?
        exp_val = 26
        act_val = info.Count
        self.assertEqual(exp_val, act_val)

 
if __name__ == '__main__':
    unittest.main()
