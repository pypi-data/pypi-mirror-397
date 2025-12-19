# Standard
import unittest
import logging
from pathlib import Path
import os

# Local
from BlackjackSim.BlackJackSim import BlackJackSim, BlackJackCheck, BlackJackGameOutcome, GamePlayOutcome
from BlackjackSim.PlayStrategy import BlackJackPlayStatus, CasinoDealerPlayStrategy, HoylePlayerPlayStrategy
from HandsDecksCards.deck import StackedDeck
from HandsDecksCards.hand import Hand
from HandsDecksCards.card import Card


class Test_Sim(unittest.TestCase):

    def test_set_player_play_strategy(self):
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        ps = CasinoDealerPlayStrategy()
        bjs.set_player_play_strategy(ps)
        
        # Did the player play strategy get set as expected?
        self.assertIsInstance(bjs._player_play_strategy, CasinoDealerPlayStrategy)
        
        # Construct something that is NOT a PlayStrategy, and try to set it as one
        ps = Card()
        self.assertRaises(AssertionError, bjs.set_player_play_strategy, ps)
        
    
    def test_set_dealer_play_strategy(self):
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        ps = HoylePlayerPlayStrategy()
        bjs.set_dealer_play_strategy(ps)
        
        # Did the dealer play strategy get set as expected?
        self.assertIsInstance(bjs._dealer_play_strategy, HoylePlayerPlayStrategy)
        
        # Construct something that is NOT a PlayStrategy, and try to set it as one
        ps = Card()
        self.assertRaises(AssertionError, bjs.set_dealer_play_strategy, ps)
        
    
    def test_get_dealer_show(self):
        bjs = BlackJackSim()
        
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','5'), Card('H','2')])
        
        # Is the dealer's show card as expected?
        c = Card('S','5')
        sc = bjs.get_dealer_show()
        
        exp_val = (c.suit, c.pips)
        act_val = (sc.suit, sc.pips)
        self.assertTupleEqual(exp_val, act_val)
        
       
    def test_draw_for_dealer(self):
        bjs = BlackJackSim()
        
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','4')])
        
        # Replace sim's deck with StackedDeck
        bjs.switch_deck(sd)

        # Draw a card
        dc = bjs.draw_for_dealer(1)
        dc = dc[0]
        
        # Did we get the one we expected?
        c = Card('C', 'A')
        exp_val = (c.suit, c.pips)
        act_val = (dc.suit, dc.pips)
        self.assertTupleEqual(exp_val, act_val)
        

    def test_draw_for_player(self):
        bjs = BlackJackSim()
        
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','4')])
        
        # Replace sim's deck with StackedDeck
        bjs.switch_deck(sd)

        # Draw a card
        dc = bjs.draw_for_player(1)
        dc = dc[0]
        
        # Did we get the one we expected?
        c = Card('C', 'A')
        exp_val = (c.suit, c.pips)
        act_val = (dc.suit, dc.pips)
        self.assertTupleEqual(exp_val, act_val)
 
    
    def test_split_has_blackjack(self):
        bjs = BlackJackSim()
         
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','4')])
        
        # Replace sim's deck with StackedDeck
        bjs.switch_deck(sd)

        # Draw 2 cards
        dc = bjs.draw_for_split(2)
        
        # Did the split hand draw blackjack?
        exp_val = True
        act_val = bjs.split_has_blackjack()
        self.assertEqual(exp_val, act_val)
       

    def test_split_does_not_have_blackjack(self):
        bjs = BlackJackSim()
         
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','9'), Card('S','4')])
        
        # Replace sim's deck with StackedDeck
        bjs.switch_deck(sd)

        # Draw 2 cards
        dc = bjs.draw_for_split(2)
        
        # Did the split hand draw blackjack?
        exp_val = False
        act_val = bjs.split_has_blackjack()
        self.assertEqual(exp_val, act_val)


    def test_draw_for_split(self):
        bjs = BlackJackSim()
        
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','4')])
        
        # Replace sim's deck with StackedDeck
        bjs.switch_deck(sd)

        # Draw a card
        dc = bjs.draw_for_split(1)
        dc = dc[0]
        
        # Did we get the one we expected?
        c = Card('C', 'A')
        exp_val = (c.suit, c.pips)
        act_val = (dc.suit, dc.pips)
        self.assertTupleEqual(exp_val, act_val)
    
    
    def test_check_blackjack_neither(self):
        
        bjs = BlackJackSim()
        
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','5'), Card('H','2')])
        
        # Set up player hand
        bjs._player_hand.add_cards([Card('C','K'), Card('D','Q')])
        
        act_val = bjs.check_for_blackjack()
        
        # Do we have the expected status?
        exp_val = BlackJackCheck.PLAY_ON
        self.assertEqual(exp_val, act_val)
 
    
    def test_check_blackjack_dealer(self):
        
        bjs = BlackJackSim()
        
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','A'), Card('H','J')])
        
        # Set up player hand
        bjs._player_hand.add_cards([Card('C','K'), Card('D','Q')])
        
        act_val = bjs.check_for_blackjack()
        
        # Do we have the expected status?
        exp_val = BlackJackCheck.DEALER_BLACKJACK
        self.assertEqual(exp_val, act_val)        


    def test_check_blackjack_player(self):
        
        bjs = BlackJackSim()
        
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','5'), Card('H','2')])
        
        # Set up player hand
        bjs._player_hand.add_cards([Card('C','K'), Card('D','A')])
        
        act_val = bjs.check_for_blackjack()
        
        # Do we have the expected status?
        exp_val = BlackJackCheck.PLAYER_BLACKJACK
        self.assertEqual(exp_val, act_val)        


    def test_check_blackjack_both(self):
        
        bjs = BlackJackSim()
        
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','10'), Card('H','A')])
        
        # Set up player hand
        bjs._player_hand.add_cards([Card('C','K'), Card('D','A')])
        
        act_val = bjs.check_for_blackjack()
        
        # Do we have the expected status?
        exp_val = BlackJackCheck.BOTH_BLACKJACK
        self.assertEqual(exp_val, act_val)        

    
    def test_play_dealer_hand_hit_to_stand(self):
        
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','5'), Card('H','2')])
        
        # Play the dealer hand
        info = bjs.play_dealer_hand()
        
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
        

    def test_play_games_fixed_player_deal_and_dealer_show(self):
        from random import seed
        seed(1234567890)
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        player_deal=[Card('H','J'), Card('S','9')]
        dealer_show=Card('D','7')
        info = sim.play_games(100, player_deal, dealer_show)
        dw = info.Dealer_Wins
        pw = info.Player_Wins
        pu = info.Pushes
        dbj = info.Dealer_BlackJacks
        pbj = info.Player_BlackJacks
        # Do we have the expected dealer wins?
        exp_val = 7
        act_val = dw
        self.assertEqual(exp_val, act_val)
        # Do we have the expected player wins?
        exp_val = 79
        act_val = pw
        self.assertEqual(exp_val, act_val)
        # Do we have the expected pushes?
        exp_val = 14
        act_val = pu
        self.assertEqual(exp_val, act_val)
        # Do we have the expected dealer BlackJacks?
        exp_val = 0
        act_val = dbj
        self.assertEqual(exp_val, act_val)
        # Do we have the expected player BlackJacks?
        exp_val = 0
        act_val = pbj
        self.assertEqual(exp_val, act_val)
    
        
    def test_play_batches_of_games(self):
        from random import seed
        seed(1234567890)
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        (results_list, net_expected, stats) = sim.play_batches_of_games(10, 10)
        
        # Did we win a net of 1 game the number of times expected?
        exp_val = 3
        match = [tup for tup in results_list if tup[0] == 1]
        act_val = match[0][1]
        self.assertEqual(exp_val, act_val)
        
        # Is this the expected fraction of times the net was 1 game?
        exp_val = 3.0/10.0
        act_val = match[0][2]
        self.assertEqual(exp_val, act_val)
        
        # Did we get the expected "expected value" for a batch of games?
        exp_val = -0.4
        act_val = net_expected
        self.assertEqual(exp_val, act_val)
        
        # Did we get (almost, to 4 decimal places) the expected values for the batch of games statistics?
        exp_val = 46.8333
        self.assertAlmostEqual(exp_val, stats.Dealer_Win_Percent_Mean, 4)
        exp_val = 4.6776
        self.assertAlmostEqual(exp_val, stats.Dealer_Win_Percent_StdErr, 4)
        exp_val = 43.3333
        self.assertAlmostEqual(exp_val, stats.Player_Win_Percent_Mean, 4)
        exp_val = 3.8490
        self.assertAlmostEqual(exp_val, stats.Player_Win_Percent_StdErr, 4)
        exp_val = 9.8333
        self.assertAlmostEqual(exp_val, stats.Push_Percent_Mean, 4)
        exp_val = 2.1148
        self.assertAlmostEqual(exp_val, stats.Push_Percent_StdErr, 4)
        exp_val = 3.0000
        self.assertAlmostEqual(exp_val, stats.Dealer_BlackJack_Percent_Mean, 4)
        exp_val = 2.1344
        self.assertAlmostEqual(exp_val, stats.Dealer_BlackJack_Percent_StdErr, 4)
        exp_val = 5.0000
        self.assertAlmostEqual(exp_val, stats.Player_BlackJack_Percent_Mean, 4)
        exp_val = 2.6874
        self.assertAlmostEqual(exp_val, stats.Player_BlackJack_Percent_StdErr, 4)
        
    
    def test_logging_info(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Set up logging
        sim.setup_logging()
        
        # Test that logger works as expected
        with self.assertLogs('blackjack_logger', level=logging.INFO) as cm:
            sim.play_games(10)
        
        # Test that the info messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'INFO:blackjack_logger:Game playing progress (%): 10')    
        self.assertEqual(cm.output[1], 'INFO:blackjack_logger:Game playing progress (%): 20')
        
    
    def test_logging_debug(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Set up logging
        sim.setup_logging()
        
        # Test that logger works as expected
        with self.assertLogs('blackjack_logger', level=logging.DEBUG) as cm:
            sim.play_game([Card('H','8'), Card('S','8')], Card('C','2'))
        
        # Test that the debug messages sent to the logger are as expected
        self.assertEqual(cm.output[0], 'DEBUG:blackjack_logger:Player has a pair and could split: 8H 8S Dealer shows: 2')    
        self.assertEqual(cm.output[1], 'DEBUG:blackjack_logger:Player chose to split.')


    def test_logging_hit_stand(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Set up logging
        sim.setup_logging()
   
        # TODO: Investigate if the generalization below will work on LINUX
        # We will always use a temporary log file name with a random component, placed in the user's Documents directory.
        home_path = Path().home().joinpath('Documents', 'temp_blackjack_' + os.urandom(8).hex() + '.log')
        fh = sim.setup_hit_stand_logging_file_handler(str(home_path))

        # Test that logger works as expected
        with self.assertLogs('blackjack_logger.hit_stand_logger', level=logging.INFO) as cm:
            # Definitely want this to be an immediate STAND, so we know what to expect in the log
            sim.play_game([Card('H','9'), Card('S','K')], Card('C','2'))
        
            # Test that the debug message sent to the logger is as expected
            self.assertEqual(cm.output[0], 'INFO:blackjack_logger.hit_stand_logger:9H KS,2C,STAND')
        
        # Clean up
        logging.getLogger('blackjack_logger.hit_stand_logger').removeHandler(fh)
        fh.close()
        os.unlink(str(home_path))
        
        # Did the file get deleted?
        self.assertTrue(not home_path.exists())

       
    def test_play_games(self):
        from random import seed
        seed(1234567890)
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        info = sim.play_games(100)
        dw = info.Dealer_Wins
        pw = info.Player_Wins
        pu = info.Pushes
        dbj = info.Dealer_BlackJacks
        pbj = info.Player_BlackJacks
        # Do we have the expected dealer wins?
        exp_val = 48
        act_val = dw
        self.assertEqual(exp_val, act_val)
        # Do we have the expected player wins?
        exp_val = 44
        act_val = pw
        self.assertEqual(exp_val, act_val)
        # Do we have the expected pushes?
        exp_val = 10
        act_val = pu
        self.assertEqual(exp_val, act_val)
        # Do we have the expected dealer BlackJacks?
        exp_val = 3
        act_val = dbj
        self.assertEqual(exp_val, act_val)
        # Do we have the expected player BlackJacks?
        exp_val = 5
        act_val = pbj
        self.assertEqual(exp_val, act_val)
        
        
    def test_play_game_with_dealer_show_specified(self):
            
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give the first card in deck to dealer, to supplement dealer_show
        sd.add_cards([Card('D','J'), Card('S','5'), Card('H','2')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game(dealer_show=Card('C','A'))
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '5S 2H'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.NONE
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 0
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)

    
    def test_play_game_with_dealer_show_and_player_deal_all_specified(self):
            
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give the first card in deck to dealer, to supplement dealer_show,
        # and no cards in deck to player to supplement player_deal.
        sd.add_cards([Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game(player_deal=[Card('S','5'), Card('H','2')],dealer_show=Card('C','A'))
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '5S 2H'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.NONE
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 0
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)

        
    def test_play_game_with_dealer_show_and_player_deal_part_specified(self):
            
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give the first card in deck to dealer, to supplement dealer_show,
        # and second card in deck to player to supplement player_deal.
        sd.add_cards([Card('D','J'), Card('H','2')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game(player_deal=[Card('S','5')],dealer_show=Card('C','A'))
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '5S 2H'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.NONE
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 0
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)
       
    
    def test_play_dealer_hand_hit_to_bust_max_stand_min(self):
        
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','7'), Card('H','9')])
        
        # Play the dealer hand
        info = bjs.play_dealer_hand()
        
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

    
    def test_play_dealer_hand_hit_to_bust_max_hit_to_stand_min(self):
        
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','3')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','7'), Card('H','8')])
        
        # Play the dealer hand
        info = bjs.play_dealer_hand()
        
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

    def test_play_dealer_hand_hit_to_bust_max_hit_to_bust_min(self):
        
        bjs = BlackJackSim(dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        # Set up dealer hand
        bjs._dealer_hand.add_cards([Card('S','7'), Card('H','8')])
        
        # Play the dealer hand
        info = bjs.play_dealer_hand()
        
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
    
    
    def test_play_player_hand(self):
        
        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        sd.add_cards([Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        # Set up dealer hand because play strategy may need a show Card
        bjs._dealer_hand.add_cards([Card('S','10'), Card('H','7')])
        
        # Set up player hand
        bjs._player_hand.add_cards([Card('S','5'), Card('H','2')])
        
        # Play the player's hand
        info = bjs.play_player_hand()
        
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
        
    
    def test_play_game_dealer_blackjack(self):

        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give first two cards in deck to dealer.
        sd.add_cards([Card('C','A'), Card('D','J'), Card('S','5'), Card('H','2')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game()
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '5S 2H'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.NONE
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 0
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)

    
    def test_play_game_player_blackjack(self):

        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give first two cards in deck to dealer.
        sd.add_cards([Card('S','5'), Card('H','2'), Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game()
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.PLAYER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '5S 2H'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
     
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.NONE
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 0
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)


    def test_play_game_both_blackjack(self):

        bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Replace sim's deck with StackedDeck
        # Create a StackedDeck
        sd = StackedDeck()
        # It's assumed that BlackJackSim.play_game() will give first two cards in deck to dealer.
        sd.add_cards([Card('S','10'), Card('H','A'), Card('C','A'), Card('D','J')])
        # Replace sim's deck with the StackedDeck
        bjs.switch_deck(sd)
       
        info = bjs.play_game()
 
        # Do we have the expected game outcome?
        exp_val = BlackJackGameOutcome.PUSH
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final hands?
        exp_val = 'AC JD'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)
       
        exp_val = '10S AH'
        act_val = info.Dealer_Final_Hand
        self.assertEqual(exp_val, act_val)
     
        # Do we have the expected statuses?
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Player_Status
        self.assertEqual(exp_val, act_val)
        
        exp_val = BlackJackPlayStatus.BLACKJACK
        act_val = info.Dealer_Status
        self.assertEqual(exp_val, act_val)
        
        # Do we have the expected final counts?
        exp_val = 21
        act_val = info.Player_Count
        self.assertEqual(exp_val, act_val)
        
        exp_val = 21
        act_val = info.Dealer_Count
        self.assertEqual(exp_val, act_val)
        
    def test_game_with_split(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        info = GamePlayOutcome()

        # Here is what will happen to the cards in the stacked deck
        # 1,2 dealt to dealer
        # 3,4 dealt to player before split
        # 5 dealt to player's split hand
        # 6 dealt to player's original hand after split
        sd = StackedDeck()
        sd.add_cards([Card('H','7'), Card('D','10'),Card('C','8'), Card('S','8'),Card('S','A'), Card('C','J')])
        sim.switch_deck(sd)
        
        # Play the game, which should result in a split
        info = sim.play_game()
        
        # Do we have the expected results for the first player hand
        exp_val = '8C JC'
        act_val = info.Player_Final_Hand
        self.assertEqual(exp_val, act_val)

        # Do we have the expected results for the second, split, player hand
        exp_val = '8S AS'
        act_val = info.Split_Final_Hand
        self.assertEqual(exp_val, act_val)
        
        
    
    def test_determine_game_outcome(self):
        
        sim = BlackJackSim()
        
        info = GamePlayOutcome()

        # Test dealer busts...
        
        info.Player_Status = BlackJackPlayStatus.STAND
        info.Player_Count = 0
        info.Dealer_Status = BlackJackPlayStatus.BUST
        info.Dealer_Count = 0
        info.Split_Status = BlackJackPlayStatus.STAND
        info.Split_Count = 0
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.PLAYER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)
 
        # Test player and split bust...

        info.Player_Status = BlackJackPlayStatus.BUST
        info.Player_Count = 0
        info.Dealer_Status = BlackJackPlayStatus.STAND
        info.Dealer_Count = 0
        info.Split_Status = BlackJackPlayStatus.BUST
        info.Split_Count = 0 
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Test all stand, player and split have high score...

        info.Player_Status = BlackJackPlayStatus.STAND
        info.Player_Count = 19
        info.Dealer_Status = BlackJackPlayStatus.STAND
        info.Dealer_Count = 17
        info.Split_Status = BlackJackPlayStatus.STAND
        info.Split_Count = 18
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.PLAYER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)

        # Test all stand, dealer has high score...

        info.Player_Status = BlackJackPlayStatus.STAND
        info.Player_Count = 19
        info.Dealer_Status = BlackJackPlayStatus.STAND
        info.Dealer_Count = 20
        info.Split_Status = BlackJackPlayStatus.STAND
        info.Player_Count = 18
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Test all stand, tie scores...

        info.Player_Status = BlackJackPlayStatus.STAND
        info.Player_Count = 19
        info.Dealer_Status = BlackJackPlayStatus.STAND
        info.Dealer_Count = 19
        info.Split_Status = BlackJackPlayStatus.STAND
        info.Split_Count = 19
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.PUSH
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)
        
        # Test all bust, it's wins by the dealer...

        info.Player_Status = BlackJackPlayStatus.BUST
        info.Player_Count = 0
        info.Dealer_Status = BlackJackPlayStatus.BUST
        info.Dealer_Count = 0
        info.Split_Status = BlackJackPlayStatus.BUST
        info.Split_Count = 0
        
        sim.determine_game_outcome(info)
            
        # Do we have the expected game and split game outcomes?
        exp_val = BlackJackGameOutcome.DEALER_WINS
        act_val = info.Game_Outcome
        self.assertEqual(exp_val, act_val)
        act_val = info.Split_Game_Outcome
        self.assertEqual(exp_val, act_val)

    
    def test_win_probability_hit_stand_dealer_blackjack(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 to obtain a blackjack
        sd.add_cards([Card('H','Q')])
        
        dealer_hand = Hand()
        # Dealer will hit on 10, then stand on 20
        dealer_hand.add_cards([Card('D','A')])
    
        player_hand = Hand()
        # Makes no difference, because dealer drew blackjack
        player_hand.add_cards([Card('S','K'),Card('C','6')])
        
        exp_val = (0.0, 0.0, 0.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val)


    def test_win_probability_hit_push_stand_lose(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 to complete deal, and then #2 to hit, and then stand
        # Player's hit will be #3
        sd.add_cards([Card('H','4'), Card('D','10'), Card('S','4')])
        
        dealer_hand = Hand()
        # Dealer will hit on 10, then stand on 20
        dealer_hand.add_cards([Card('D','6')])
    
        player_hand = Hand()
        # When player stands on 16 they will lose
        # When player hits to 20 they will push
        player_hand.add_cards([Card('S','K'),Card('C','6')])
        
        exp_val = (0.0, 0.0, 1.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val) 
 
    
    def test_win_probability_hit_lose_stand_push(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 and then stand
        # Player's hit will be #2
        sd.add_cards([Card('D','10'), Card('S','4')])
        
        dealer_hand = Hand()
        # Dealer will hit on 10, then stand on 20
        dealer_hand.add_cards([Card('D','6'),Card('H','4')])
    
        player_hand = Hand()
        # When player stands on 20 they will push
        # When player hits to 24 (bust) they will lose
        player_hand.add_cards([Card('S','K'),Card('C','Q')])
        
        exp_val = (0.0, 0.0, 0.0, 1.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val) 
        

    def test_win_probability_hit_lose_stand_lose(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 and then stand
        # Player's hit will be #2
        sd.add_cards([Card('D','10'), Card('S','2')])
        
        dealer_hand = Hand()
        # Dealer will hit on 10, then stand on 20
        dealer_hand.add_cards([Card('D','6'),Card('H','4')])
    
        player_hand = Hand()
        # When player stands on 16 they will lose
        # When player hits to 18 they will win
        player_hand.add_cards([Card('S','K'),Card('C','6')])
        
        exp_val = (0.0, 0.0, 0.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val)

    
    def test_win_probability_hit_win_stand_win(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 and then stand
        # Player's hit will be #2
        sd.add_cards([Card('D','9'), Card('S','2')])
        
        dealer_hand = Hand()
        # Dealer will hit on 8, then stand on 17
        dealer_hand.add_cards([Card('D','6'),Card('H','2')])
    
        player_hand = Hand()
        # When player stands on 18 they will win
        # When player hits to 20 they will win
        player_hand.add_cards([Card('S','K'),Card('C','8')])
        
        exp_val = (1.0, 1.0, 0.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val)
       

    def test_win_probability_hit_lose_stand_win(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 and then stand
        # Player's hit will be #2
        sd.add_cards([Card('D','9'), Card('S','4')])
        
        dealer_hand = Hand()
        # Dealer will hit on 8, then stand on 17
        dealer_hand.add_cards([Card('D','6'),Card('H','2')])
    
        player_hand = Hand()
        # When player stands on 18 they will win
        # When player hits to bust (22) they will lose
        player_hand.add_cards([Card('S','K'),Card('C','8')])
        
        exp_val = (0.0, 1.0, 0.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val)
        
        
    def test_win_probability_hit_win_stand_lose(self):
        
        sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
        
        # Create a StackedDeck
        sd = StackedDeck()
        # Dealer will draw #1 and then stand
        # Player's hit will be #2
        sd.add_cards([Card('D','10'), Card('S','2')])
        
        dealer_hand = Hand()
        # Dealer will hit on 8, then stand on 18
        dealer_hand.add_cards([Card('D','6'),Card('H','2')])
    
        player_hand = Hand()
        # When player stands on 17 they will lose
        # When player hits to 19 they will win
        player_hand.add_cards([Card('S','K'),Card('C','7')])
        
        exp_val = (1.0, 0.0, 0.0, 0.0) # (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
        act_val = sim.win_probability_hit_stand(player_hand,dealer_hand,1,sd)

        self.assertTupleEqual(exp_val, act_val)
        
    def test_percent_done(self):
        sim = BlackJackSim()
        
        (report, percent_done) = sim.percent_done(9546, 954)
        
        # Did we get that we should report?
        act_val = report
        exp_val = True
        self.assertEqual(exp_val, act_val)
        
        # Did we get 10% ?
        act_val = percent_done
        exp_val = 10
        self.assertEqual(exp_val, act_val)
        
        (report, percent_done) = sim.percent_done(9546, 2387)
        
        # Did we get that we should not report?
        act_val = report
        exp_val = False
        self.assertEqual(exp_val, act_val)
        
        # Did we get 25% ?
        act_val = percent_done
        exp_val = 25
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
