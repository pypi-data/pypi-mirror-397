"""
Defines the BlackJackSim class, which represents a Blackjack game to be played by one player (human or computer)
and one dealer (always computer).

Exported Classes:
    BlackJackCheck - An enumeration returned by BlackJackSim._check_for_blackjack().
    BlackJackGameOutcome - An enumeration representing outcomes of playing a game of Blackjack, that is, who won.
    GamePlayOutcome - A structured way of returning detailed information about the outcome of a game of BlackJack.
    BlackJackStats - A structured way of returning statistical information about the results of playing many games of Blackjack.
    BlackJackBatchStats - A structured way of returning information about the results of playing batches of games of BlackJack.
    BlackJackSim - Represents a Blackjack game and contains the game playing logic.

Exported Exceptions:
    None    
 
Exported Functions:
    None

Logging:
    Uses a logger named 'blackjack_logger' for providing game output to the user. This logger is configured
    by calling BlackJackSim.setup_logging(...).
 """


# Standard imports
from enum import Enum
import logging
from statistics import mean, stdev
from math import sqrt

# Local imports
from HandsDecksCards.deck import Deck
from HandsDecksCards.hand import Hand
from BlackjackSim.PlayStrategy import BlackJackPlayStatus, PlayStrategy


class BlackJackCheck(Enum):
    """
    An enumeration returned by BlackJackSim.check_for_blackjack().
    """
    PLAY_ON = 1
    DEALER_BLACKJACK = 2
    PLAYER_BLACKJACK = 3
    BOTH_BLACKJACK = 4


class BlackJackGameOutcome(Enum):
    """
    An enumeration that is part of the object that represents the outcome of playing a game.
    """
    PLAYER_WINS = 1
    DEALER_WINS = 2
    # PUSH means both blackjack, bust, or stand with a tie count
    PUSH = 3
    # NONE means that the hand used to play the second hand of a split pair was not used in the game, that is, no pair was split
    NONE = 4


class GamePlayOutcome:
    """
    This class is a structured way of returning information about the outcome of playing a game of black jack, e.g., from play_game().
    Think of this as a C struct, where it is expected that data members will be direcly accessed, because this class has no methods, beyound __init__().
    """
    def __init__(self):
        """
        Create the data members of structured info.
            Dealer_Final_Hand = String representation of dealer's hand of cards at the end of the game, string
            Dealer_Status = 'bust', 'stand', 'blackjack', or 'none' (player blackjacked, dealer didn't), BlackJackPlayStatus Enum
            Dealer_Count = Final count of dealer's hand (0 if player blackjacked and dealer didn't), int
            Player_Final_Hand = String representation of Player's hand of cards at the end of the game, string
            Player_Status = 'bust', 'stand', 'blackjack', or 'none'  (dealer blackjacked, player didn't), BlackJackPlayStatus Enum
            Player_Count = Final count of Player's hand (0 if dealer blackjacked and player didn't), int
            Split_Final_Hand = String representation of Player's split hand of cards at the end of the game, string
                (Empty if player's hand is not split.)
            Split_Status = 'bust', 'stand', 'blackjack', or 'none'  (dealer blackjacked, player didn't), BlackJackPlayStatus Enum
                ('none' if player's hand is not split.)
            Split_Count = Final count of Player's split hand (0 if dealer blackjacked and player didn't), int
                (0 if player's hand is not split.)
            Game_Outcome = Who won?, BlackJackGameOutcome() enum
            Split_Game_Outcome = Who won the split game?, BlackJackGameOutcome() enum
        """
        self.Dealer_Final_Hand = ''
        self.Dealer_Status = BlackJackPlayStatus.STAND
        self.Dealer_Count = 0
        self.Player_Final_Hand = ''
        self.Player_Status = BlackJackPlayStatus.STAND
        self.Player_Count = 0
        self.Split_Final_Hand = ''
        self.Split_Status = BlackJackPlayStatus.NONE
        self.Split_Count = 0
        self.Game_Outcome = BlackJackGameOutcome.PUSH
        self.Split_Game_Outcome = BlackJackGameOutcome.NONE
    

class BlackJackStats:
    """
    This class is a structured way of returning information about the outcome of playing many games of black jack, e.g., from play_games().
    Think of this as a C struct, where it is expected that data members will be direcly accessed, because this class has no methods, beyound __init__().
    """
    def __init__(self):
        """
        Create the data members of structured info.
            Dealer_Wins = The number of games won by the dealer, int
            Player_WIns = The number of games won by the player, int
            Pushes = The number of tie (push) games, int
            Dealer_BlackJacks = The number of games where the dealer was dealt BlackJack, int
            Player_BlackJacks = The number of games where teh player was dealt BlackJack, int
            Notes:
                If a dealer is dealt BlackJack, then Dealer_Wins +=1 and Dealer_BlackJacks +=1
                If a player is dealt BlackJack, and the Dealer isn't, then Player_Wins +=1, and Player_BlackJacks +=1
                If both player and dealer are dealt BlackJack, then Pushes +=1, Dealer_BlackJacks +=1, PlayerBlackJacks +=1
        """
        self.Dealer_Wins = 0
        self.Player_Wins = 0
        self.Pushes = 0
        self.Dealer_BlackJacks = 0
        self.Player_BlackJacks = 0

        
class BlackJackBatchStats:
    """
    This class is a structued way of returning information about the out come of playing batches of blackjack, e.g., from play_batches_of_games().
    Think of this as a C struct, where it is expected that data members will be direcly accessed, because this class has no methods, beyound __init__().
    """
    
    def __init__(self):
        """
        Create the data members of the structured info.
            The mean values of the win/push/blackjack percents from each batch of games: 
                Dealer_Win_Percent_Mean
                Player_Win_Percent_Mean
                Push_Percent_Mean
                Dealer_BlackJack_Percent_Mean
                Player_BlackJack_Percent_Mean
            The standard error of the mean values of the win/push/blackjack percents from each batch of games:
            (For definition of standard error: https://en.wikipedia.org/wiki/Standard_error)
                Dealer_Win_Percent_StdErr
                Player_Win_Percent_StdErr
                Push_Percent_StdErr
                Dealer_BlackJack_Percent_StdErr
                Player_BlackJack_Percent_StdErr
        """
        self.Dealer_Win_Percent_Mean = 0.0
        self.Dealer_Win_Percent_StdErr = 0.0
        self.Player_Win_Percent_Mean = 0.0
        self.Player_Win_Percent_StdErr = 0.0
        self.Push_Percent_Mean = 0.0
        self.Push_Percent_StdErr = 0.0
        self.Dealer_BlackJack_Percent_Mean = 0.0
        self.Dealer_BlackJack_Percent_StdErr = 0.0
        self.Player_BlackJack_Percent_Mean = 0.0
        self.Player_BlackJack_Percent_StdErr = 0.0


class BlackJackSim:
    """
    Logic for playing a game of black jack.
    """
    def __init__(self, player_strategy = PlayStrategy(), dealer_strategy = PlayStrategy()):
        """
        Construct an infinite deck of Cards (i.e. an infinite deck shute), an empty dealer Hand, an empty player Hand,
        and, to be used if needed, an empty hand for if the player splits a pair. Also set strategies for dealer and player hand play.
        :parameter player_strategy: PlayStrategy instance used to play player hand, PlayStrategy or child instance
        :parameter dealerer_strategy: PlayStrategy instance used to play dealer hand, PlayStrategy or child instance
        """
        self._deck = Deck(isInfinite = True)
        self._dealer_hand = Hand()
        self.set_dealer_play_strategy(dealer_strategy)
        self._player_hand = Hand()
        self._split_hand = Hand() # For if the player splits a pair
        self.set_player_play_strategy(player_strategy)
        
    # TODO: Add ability to log detailed results of all individual games in a set to a text file for later analyis.
    
    def set_player_play_strategy(self, ps = PlayStrategy()):
        """
        Set the player play strategy.
        :parameter ps: The player play strategy, PlayStrategy()
        :return: None
        """
        assert(isinstance(ps, PlayStrategy))
        self._player_play_strategy = ps
        return None
            
    def set_dealer_play_strategy(self, ps = PlayStrategy()):
        """
        Set the dealer play strategy.
        :parameter ps: The dealer play strategy, PlayStrategy()
        :return: None
        """
        assert(isinstance(ps, PlayStrategy))
        self._dealer_play_strategy = ps
        return None
                    
    def switch_deck(self, new_deck = Deck(isInfinite = True)):
        """
        Replace the current deck with a new deck. Intended mainly to faciliatate testing, where it is helpful to use a StackedDeck().
        :parameter new_deck: The new Deck() to assign to the simulator, Deck()
        :return: None
        """
        self._deck = new_deck
        return None
            
    def draw_for_dealer(self, number=1):
        """
        Draw one or more cards from deck into dealer's hand.
        :parameter number: How many cards to draw into dealer's hand, int
        :return: A list of Card(s) in the hand after the draw
        """
        return self._dealer_hand.add_cards(self._deck.draw(number))
        
    def dealer_hand_info(self):
        """
        Call Hand.hand_info on the dealer's hand.
        :return: Hand.HandInfo object with useful information about the dealer's hand.
        """
        return self._dealer_hand.hand_info()
    
    def player_hand_info(self):
        """
        Call Hand.hand_info on the player's hand.
        :return: Hand.HandInfo object with useful information about the player's hand.
        """
        return self._player_hand.hand_info()

    def split_hand_info(self):
        """
        Call Hand.hand_info on the player's split hand.
        :return: Hand.HandInfo object with useful information about the player's split hand.
        """
        return self._split_hand.hand_info()    
        
    def draw_for_player(self, number=1):
        """
        Draw one or more cards from deck into player's hand.
        :parameter number: How many cards to draw into player's hand, int
        :return: A list of Card(s) in the hand after the draw
        """
        return self._player_hand.add_cards(self._deck.draw(number))
    
    def draw_for_split(self, number=1):
        """
        Draw one or more cards from deck into player's split hand.
        :parameter number: How many cards to draw into player's split hand, int
        :return: A list of Card(s) in the hand after the draw
        """
        return self._split_hand.add_cards(self._deck.draw(number))   
    
    def get_dealer_show(self):
        """
        Return the dealer's face up (show) card that can be seen by the player.
        :return: The first card in the dealer's hand, Card()
        """
        return self._dealer_hand.get_cards()[0]
    
    def play_batches_of_games(self, num_games = 1, num_batches = 1):
        """
        Play multiple batches of multiple games of blackjack. The intent is to, for example, answer the qestion of what is
        the distribution of +/- player games won if 20 games are played in a batch, and thousands of batches are played.
        This would correspond to, for example, sitting at a $5 blackjack table in vegas and playing 20 hands.
        What then is the probability of losing or winning a net of X games at a sitting.
        :parameter num_games: Number of games to be played for each batch, int
        :parameter num_batches: Number of batches of games to be played, int
        :return: A tuple:
            Item 1: An ordered list of tuples where the first value is the int number of net losses (-) or wins (+), the second value
            is the number of batches that produced this net number of losses or wins, and the third value is the fraction of batches
            that produced this net number of losses or wins.
            Item 2: The expected value of net losses or wins.
            Item 3: Statistics across the batches, BlackJackBatchStats object
        """        
        # Get the logger 'blackjack_logger'
        logger = logging.getLogger('blackjack_logger')

        results = {}
        
        # Accumulate the number of batches using a dictionary, since we don't know which values of net wins or losses will show up
        
        stats_list = []
        for b in range(num_batches):

            # Occassionally report progress by info logging
            (report, percent_done) = self.percent_done(num_batches, b+1) # The +1 puts the counting for messaging on a 1...N basis instead of 0...N-1
            if report:
                msg = 'Batch playing progress (%): ' + str(percent_done)
                logger.info(msg)

            batch_stats = self.play_games(num_games)
            net_wins = batch_stats.Player_Wins - batch_stats.Dealer_Wins
            # Accumulate the stats for the individual batches in a list, to be returned for additional possible analysis
            stats_list.append(batch_stats)
            # Look up the results dictionary entry for key of net_wins
            v = results.get(net_wins)
            if v is None:
                # Key is not yet in the dictionary, add it now with a value of 1
                results[net_wins] = 1
            else:
                # Key is already in the dictionary. Increment value up by 1 and reset it.
                results[net_wins] = v + 1

        # Now we will iterate through the dictionary entries to create from them an ordered list of tuples (key,value,frac)
        # since providing ordered return is better than unordered.

        expected_value = 0.0
        results_list = []
        for b in range(-num_batches, num_batches+1, 1):
            # Look up the results dictionary entry for key of b
            v = results.get(b)
            if v is not None:
                # key value of b is in the dictionary, so put it and it's value in the list as a tuple
                results_list.append((b,v,1.0*v/num_batches))
                expected_value += 1.0*b*v/num_batches

        # Compile the BlackJackBatchStats return value from the stats_list (mean and standard error values)
        stats_return = BlackJackBatchStats()
        
        pwlst = [(s.Player_Wins / (s.Player_Wins + s.Dealer_Wins + s.Pushes)) for s in stats_list]
        stats_return.Player_Win_Percent_Mean = 100.0 * mean(pwlst)
        stats_return.Player_Win_Percent_StdErr = 100.0 * stdev(pwlst) / sqrt(num_batches)

        dwlst = [(s.Dealer_Wins / (s.Player_Wins + s.Dealer_Wins + s.Pushes)) for s in stats_list]
        stats_return.Dealer_Win_Percent_Mean = 100.0 * mean(dwlst)
        stats_return.Dealer_Win_Percent_StdErr = 100.0 * stdev(dwlst) / sqrt(num_batches)

        pushlst = [(s.Pushes / (s.Player_Wins + s.Dealer_Wins + s.Pushes)) for s in stats_list]
        stats_return.Push_Percent_Mean = 100.0 * mean(pushlst)
        stats_return.Push_Percent_StdErr = 100.0 * stdev(pushlst) / sqrt(num_batches)
    
        pbjlst = [(s.Player_BlackJacks / (s.Player_Wins + s.Dealer_Wins + s.Pushes)) for s in stats_list]
        stats_return.Player_BlackJack_Percent_Mean = 100.0 * mean(pbjlst)
        stats_return.Player_BlackJack_Percent_StdErr = 100.0 * stdev(pbjlst) / sqrt(num_batches)

        dbjlst = [(s.Dealer_BlackJacks / (s.Player_Wins + s.Dealer_Wins + s.Pushes)) for s in stats_list]
        stats_return.Dealer_BlackJack_Percent_Mean = 100.0 * mean(dbjlst)
        stats_return.Dealer_BlackJack_Percent_StdErr = 100.0 * stdev(dbjlst) / sqrt(num_batches)
                
        return (results_list, expected_value, stats_return)
    
    def play_games(self, num_games = 1, player_deal = [], dealer_show = None):
        """
        Play multiple games of blackjack, returning a BlackJackStats() object of statistics of outcomes across the set of games.
        :parameter num_games: The number of games to play, int
        :parameter player_deal: A list of no, one, or two Card()s dealt to the player. The deal will be completed with 2, 1, or no
            cards. This is intended to enable fixing part or all of the initial player hand.
        :paremeter dealer_show: If specified, it is the showing, face up Card() for the dealer, and one additional card will be
            drawn to complete the dealer's initial hand. This is intended to enable fixing the part of the dealer's hand which
            is visible to the player.
        :return: Statistics for the set of games, as a BlackJackStats() object
        """        
        # Get the logger 'blackjack_logger'
        logger = logging.getLogger('blackjack_logger')
        
        game_stats = BlackJackStats()
        
        dealer_wins = 0
        player_wins = 0
        pushes = 0
        dealer_blackjacks = 0
        player_blackjacks = 0
        
        for g in range(num_games):
            
            # Occassionally report progress by info logging
            (report, percent_done) = self.percent_done(num_games, g+1) # The +1 puts the counting for messaging on a 1...N basis instead of 0...N-1
            if report:
                msg = 'Game playing progress (%): ' + str(percent_done)
                logger.info(msg)
                
            info = self.play_game(player_deal, dealer_show)
            # Gather and record stats on who won
            if info.Game_Outcome == BlackJackGameOutcome.DEALER_WINS:
                dealer_wins += 1
            elif info.Game_Outcome == BlackJackGameOutcome.PLAYER_WINS:
                player_wins += 1
            elif info.Game_Outcome == BlackJackGameOutcome.PUSH:
                pushes += 1
            # Gather and record stats on who won the split hand if the player split a pair
            if info.Split_Game_Outcome == BlackJackGameOutcome.DEALER_WINS:
                dealer_wins += 1
            elif info.Split_Game_Outcome == BlackJackGameOutcome.PLAYER_WINS:
                player_wins += 1
            elif info.Split_Game_Outcome == BlackJackGameOutcome.PUSH:
                pushes += 1
            # Gather and record stats on getting BlackJack
            if info.Dealer_Status == BlackJackPlayStatus.BLACKJACK:
                dealer_blackjacks += 1
            if info.Player_Status == BlackJackPlayStatus.BLACKJACK:
                player_blackjacks += 1
            if info.Split_Status == BlackJackPlayStatus.BLACKJACK:
                player_blackjacks += 1
        
        game_stats.Dealer_Wins = dealer_wins
        game_stats.Player_Wins = player_wins
        game_stats.Pushes = pushes
        game_stats.Dealer_BlackJacks = dealer_blackjacks
        game_stats.Player_BlackJacks = player_blackjacks
               
        return game_stats
    
    def play_game(self, player_deal = [], dealer_show = None, dealer_down = None):
        """
        Play one game of black jack, returning a GamePlayOutcome() object of information about the outcome of the game.
        :parameter player_deal: A list of no, one, or two Card()s dealt to the player. The deal will be completed with 2, 1, or no
            cards. This is intended to enable fixing part or all of the initial player hand.
        :parameter dealer_show: If specified, it is the showing, face up Card() for the dealer, and one additional card will be
            drawn to complete the dealer's initial hand. This is intended to enable fixing the part of the dealer's hand which
            is visible to the player.
        :parameter dealer_down: If specified, it is the face down Card() for the dealer. This is intended to fix the part of the
            dealer's deal that is invisible to the player.
        :return: Information about the outcome of the game or games (if their is a split), GamePlayOutcome() object
        """        
        # Get the logger 'blackjack_logger'
        logger = logging.getLogger('blackjack_logger')
        
        info = GamePlayOutcome()
        
        # Clear dealer, player, and split hands of Cards
        self.clear_hands()
        
        # Build the dealer's initial hand, drawing as needed
        
        if dealer_show is None:
            # Draw a card for the dealer's show card
            self.draw_for_dealer(1)
        else:
            # Add the argument show card to the dealer's hand
            self._dealer_hand.add_cards(dealer_show)

        if dealer_down is None:
            # Draw a card for the dealer's down card
            self.draw_for_dealer(1)
        else:
            # Add the argument down card to the dealer's hand
            self._dealer_hand.add_cards(dealer_down)
            
        # Build the player's inital hand, drawing as needed
        assert(len(player_deal) <=2)
        self._player_hand.add_cards(player_deal)
        if len(player_deal) == 0:
            self._player_hand.add_cards(self._deck.draw(2))
        elif len(player_deal) == 1:
            self._player_hand.add_cards(self._deck.draw(1))
        
        check_info = self.check_for_blackjack()
        if check_info == BlackJackCheck.PLAY_ON:
        
            # Neither dealer nor player have blackjack, on deal, so play the hands.

            if self._player_hand.get_cards()[0].pips == self._player_hand.get_cards()[1].pips:
                # The player has been dealt a pair. Ask the player strategy if we should split.
                msg = 'Player has a pair and could split: ' + str(self._player_hand) + ' Dealer shows: ' + self.get_dealer_show().pips
                logger.debug(msg)
                if self._player_play_strategy.split(self._player_hand.get_cards()[0].pips, self.get_dealer_show().pips):
                    logger.debug('Player chose to split.')
                    # Execute split
                    
                    # Preserve second of pair to be transferred to split hand, and remove it from the player's hand
                    xfer_card = self._player_hand.remove_card()
                    # Add the preserved card to the split hand
                    self._split_hand.add_cards([xfer_card])
                    # Draw a second card into the split hand
                    self.draw_for_split(1)
                    # TODO: What if we drew to BlackJack in the split? For, now, just assert that the split does not have blackjack.
                    # A saving grace is that if the player play strategy is Hoyle, which it is by default, then the player will
                    # never split A's, faces, or 10's, meaning it isn't possible to split and draw a blackjack with that strategy. 
                    assert(not self.split_has_blackjack())
                    
                    # Draw a replacement card for the player's hand
                    self.draw_for_player(1)
                    # TODO: What if we drew to BlackJack in the player's hand? For now, just assert that the player's hand does not have blackjack.
                    # A saving grace is that if the player play strategy is Hoyle, which it is by default, then the player will
                    # never split A's, faces, or 10's, meaning it isn't possible to split and draw a blackjack with that strategy.
                    assert(self.check_for_blackjack() != BlackJackCheck.PLAYER_BLACKJACK)
                    assert(self.check_for_blackjack() != BlackJackCheck.BOTH_BLACKJACK)
                    
                    # Play the split hand, and add hand outcome info to game info

                    split_info = self.play_split_hand()
                    info.Split_Final_Hand = split_info.Final_Hand
                    info.Split_Status = split_info.Status
                    info.Split_Count = split_info.Count 

            
            # Play player hand, and add hand outcome info to game info
            player_info = self.play_player_hand()
            info.Player_Final_Hand = player_info.Final_Hand
            info.Player_Status = player_info.Status
            info.Player_Count = player_info.Count      
        
            # Play dealer hand, and add hand outcome info to game info
            dealer_info = self.play_dealer_hand()
            info.Dealer_Final_Hand = dealer_info.Final_Hand
            info.Dealer_Status = dealer_info.Status
            info.Dealer_Count = dealer_info.Count
                    
            # Determine game outcome, and add to game info
 
            self.determine_game_outcome(info)
         
        else:
            
            # One or both of dealer or/and player have blackjack. Set game outcome, etc. in game info

            info.Player_Final_Hand = str(self._player_hand)
            info.Dealer_Final_Hand = str(self._dealer_hand)
            
            if check_info == BlackJackCheck.BOTH_BLACKJACK:
                # It's a tie score, and a push
                info.Game_Outcome = BlackJackGameOutcome.PUSH
                info.Player_Status = BlackJackPlayStatus.BLACKJACK
                info.Player_Count = 21
                info.Dealer_Status = BlackJackPlayStatus.BLACKJACK
                info.Dealer_Count = 21
            elif check_info == BlackJackCheck.DEALER_BLACKJACK:
                info.Game_Outcome = BlackJackGameOutcome.DEALER_WINS
                info.Player_Status = BlackJackPlayStatus.NONE
                info.Player_Count = 0
                info.Dealer_Status = BlackJackPlayStatus.BLACKJACK
                info.Dealer_Count = 21
            elif check_info == BlackJackCheck.PLAYER_BLACKJACK:
                info.Game_Outcome = BlackJackGameOutcome.PLAYER_WINS
                info.Player_Status = BlackJackPlayStatus.BLACKJACK
                info.Player_Count = 21
                info.Dealer_Status = BlackJackPlayStatus.NONE
                info.Dealer_Count = 0

        return info
            
    def split_has_blackjack(self):
        """
        Return True if split hand has blackjack, otherwise return False.
        :return: Split hand has blackjack, True/False, bool
        """
        split_info = self._split_hand.hand_info()
        if split_info.Count_Max == 21:
            return True
        else:
            return False
            
    def check_for_blackjack(self):
        """
        Check the dealer's ane player's, hands for blackjack.
        And, based on dealer's and player's hands, declare a winner (one hand has blackjack) or a push (both hands have blackjack).
        :return: The outcome of the black jack check, BlackJackCheck() enum
        """              
        # Note that this will be the default return, that is, if none of the if/elif below are true
        check_info = BlackJackCheck.PLAY_ON
        
        dealer_info = self._dealer_hand.hand_info()
        player_info = self._player_hand.hand_info()
        
        if dealer_info.Count_Max == 21 and player_info.Count_Max == 21:
            check_info = BlackJackCheck.BOTH_BLACKJACK
        elif dealer_info.Count_Max == 21:
            check_info = BlackJackCheck.DEALER_BLACKJACK
        elif player_info.Count_Max == 21:
            check_info = BlackJackCheck.PLAYER_BLACKJACK
            
        return check_info
        
    def play_dealer_hand(self):
        """
        Play the dealer's hand of black jack, using the dealer play strategy, and returning a HandPlayOutcome() object with
        information about the outcome of playing the hand.
        :return: Information about the outcome of playing the hand, HandPlayOutcome() class object
        """
        outcome_info = self._dealer_play_strategy.play(hand_info_callback=self.dealer_hand_info, draw_callback=self.draw_for_dealer, dealer_show_callback=self.get_dealer_show)
                  
        return outcome_info
         
    def play_player_hand(self):
        """
        Play the player's hand of black jack, using the player play strategy, and returning a HandPlayOutcome() object with
        information about the outcome of playing the hand.
        :return: Information about the outcome of playing the hand, HandPlayOutcome() class object
        """
        outcome_info = self._player_play_strategy.play(hand_info_callback=self.player_hand_info, draw_callback=self.draw_for_player, dealer_show_callback=self.get_dealer_show, sim_object = self)
                    
        return outcome_info
        
    def play_split_hand(self):
        """
        Play the player's split hand of black jack, using the player play strategy, and returning a HandPlayOutcome() object with
        information about the outcome of playing the hand.
        :return: Information about the outcome of playing the hand, HandPlayOutcome() class object
        """
        outcome_info = self._player_play_strategy.play(hand_info_callback=self.split_hand_info, draw_callback=self.draw_for_split, dealer_show_callback=self.get_dealer_show, sim_object = self)

        return outcome_info
    
    def determine_game_outcome(self, info = GamePlayOutcome()):
        """
        Complete the argument info dictionary after determing the game winner.
        Assumes that Player_Status, Dealer_Status, Player_Count, and Dealer_Count exist in the info dictionary upon entry to this method.
        Assumes that Split_Count exists upon entry to this method if Split_Status != BlackJackPlayStatus.NONE
        :param info: Same info object returned by play_game(), GamePlayOutcome() object
        :return: None
        """
        # Determine game outcome for the only hand of the game, or for the first hand if there was a split of a pair by player
        if (info.Player_Status == BlackJackPlayStatus.BUST):
            # If player busts, then it doesn't matter what the dealer status is, the dealer wins.
            # This is the house's advantage in the game.
            info.Game_Outcome = BlackJackGameOutcome.DEALER_WINS
        elif (info.Player_Status == BlackJackPlayStatus.STAND) and (info.Dealer_Status == BlackJackPlayStatus.BUST):
            info.Game_Outcome = BlackJackGameOutcome.PLAYER_WINS
        else:
            # Both player and dealer stood, higher score wins
            if info.Player_Count > info.Dealer_Count:
                # Player wins
                info.Game_Outcome = BlackJackGameOutcome.PLAYER_WINS
            elif info.Player_Count < info.Dealer_Count:
                # Dealer wins
                info.Game_Outcome = BlackJackGameOutcome.DEALER_WINS
            else:
                # It's a tie score, and a push
                info.Game_Outcome = BlackJackGameOutcome.PUSH
                
        # Determine game outcome for the second, split hand, if there was a split of a pair by the player
        if (info.Split_Status != BlackJackPlayStatus.NONE):
            if (info.Split_Status == BlackJackPlayStatus.BUST):
                # If split busts, then it doesn't matter what the dealer status is, the dealer wins.
                # This is the house's advantage in the game.
                info.Split_Game_Outcome = BlackJackGameOutcome.DEALER_WINS
            elif (info.Split_Status == BlackJackPlayStatus.STAND) and (info.Dealer_Status == BlackJackPlayStatus.BUST):
                info.Split_Game_Outcome = BlackJackGameOutcome.PLAYER_WINS
            else:
                # Both split and dealer stood, higher score wins
                if info.Split_Count > info.Dealer_Count:
                    # Split wins
                    info.Split_Game_Outcome = BlackJackGameOutcome.PLAYER_WINS
                elif info.Split_Count < info.Dealer_Count:
                    # Dealer wins
                    info.Split_Game_Outcome = BlackJackGameOutcome.DEALER_WINS
                else:
                    # It's a tie score, and a push
                    info.Split_Game_Outcome = BlackJackGameOutcome.PUSH         
       
        return None
    
    def setup_logging(self):
        """
        This method configures logging. It should be called ahead of any calls to play_game(...) to ensure the expected behavior
        of logging. Though failure to do so should not be breaking.
        :return: None
        """
        # Create a logger with name 'blackjack_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        # This logger is currently intended to handle everything that isn't hit/stand data going to file.
        logger = logging.getLogger('blackjack_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr (e.g., pair dealt so split is possible)
        #   INFO = info messages sent to this logger will end up on stderr (e.g., number of current game when multiple are being played)
        logger.setLevel(logging.INFO)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(logging.DEBUG)
        # Add the stream handler to the logger
        logger.addHandler(sh)
    
        # Create the new logger that will handle hit/stand data going to file.
        # Create it as a child of the logger, 'blackjack_logger'
        logger = logging.getLogger('blackjack_logger.hit_stand_logger')
        # Set the logger's level to INFO. If this is left at the NOTSET default, then all messages would be sent to parent
        # (Except that propagate is set to False below.) 
        logger.setLevel(logging.INFO)
        # Don't propagate to parents from this logger
        logger.propagate = False
        
        return None
    
    def setup_hit_stand_logging_file_handler(self, logpath):
        """
        This method configures a file handler for logger 'blackjack_logger.hit_stand_logger'.
        It is optional to call this, but it should be called after calling the setup_logging() method.
        :parameter logpath: The path and name of the file for logging hit stand data, string with '\\' escaped
        :return: the logger.fileHandler
        """
        # Get the hit/stand data logger so we can add a file handler to it
        logger = logging.getLogger('blackjack_logger.hit_stand_logger')
        # Create a file handler to log events at this level of the logger hierarchy
        fh = logging.FileHandler(filename=logpath, mode='w')
        # Log an info message at this level of the logger, but note, since the file handler hasn't been added to the logger yet,
        # this message will not go into the logging file, which is good, since it is not hit / stand data
        msg = 'Hit/stand data will be logged to file: ' + logpath
        logging.getLogger('blackjack_logger').info(msg)
        # Set the file handler to log at INFO level, so hit/stand data needs to be injected to this logger wth logger.info(...)
        fh.setLevel(logging.INFO)
        # Create a formatter for hit/stand info, which just logs the info string itself, and add it to the file handler
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        # Add the file handler to the logger
        logger.addHandler(fh)
        # Add "header" information to the hit/stand logging file
        logger.info('%s,%s,%s', 'HAND', 'SHOW', 'CLASS' )
        
        return fh
        
    def clear_hands(self, clear_dealer = True, clear_player = True, clear_split = True):
        """
        Clear the Hand()s used for the simulation.
        :Parameter clear_dealer: If True (default), clear the dealer's hand, boolean
        :Parameter clear_player: If True (default), clear the player's hand, boolean
        :Parameter clear_split: If True (default), clear the player's split hand, boolean
        :return: None
        """
        if (clear_dealer): self._dealer_hand = Hand()
        if (clear_player): self._player_hand = Hand()
        if (clear_split): self._split_hand = Hand()

        return None
    
    def win_probability_hit_stand(self, player_hand = Hand(), dealer_hand = Hand(), num_trials = 1000, deck = None):
        """
        Determine the probability of winning and pushing for both hitting one card and for standing at any point in playing a hand.
        Assumes that dealer's hand has just been dealt with one or two cards, and that player's hand as 2+ cards. If the dealer's hand
        has one card, the typical situation, then it is considered the face up "show" card, and the hidden card will be drawn from the
        deck on each trial. In this case the function is determining probabilities based only on "known" information. If the dealer's
        hand has two cards, then, at least in a statistical sense, this function represents a "cheat" because it uses information about
        the dealer's hidden card from the deal to determine probabilities.
        :parameter player_hand: The player's hand for which stand and hit probabilities will be determined, Hand object
        :parameter dealer_hand: The dealer's had against which stand and hit wind proabilities will be determined, Hand object 
        :parameter num_trials: The number of times to hit and play out the dealer's hand to determine probabilities, int
        :parameter deck: The deck that will be used for all the trials, Deck object.
            If None, then when the new BlackJackSimulation is created for the trials, it's default Deck will be used.
            Typically this argument should not be used, unless to facilitate testing. It might also be used to replicate the remains
            of a multi-deck "shoe", in which case each trial should use the same replication.
        :return: Tuple (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob), floats
        """
        # Check assumptions
        assert(player_hand.get_num_cards() >= 2)
        assert(dealer_hand.get_num_cards() >=1 and dealer_hand.get_num_cards() <= 2)
        if (deck is not None): assert(isinstance(deck, Deck))

        # Get the logger 'blackjack_logger'
        logger = logging.getLogger('blackjack_logger')

        # Zero out some counters and stat variables
        hit_win_count = 0
        hit_push_count = 0
        stand_win_count = 0
        stand_push_count = 0
        hit_win_prob = 0.0
        hit_push_prob = 0.0
        stand_win_prob = 0.0
        stand_push_prob = 0.0

        # Create a new BlackJackSim object to be used to play the games needed to compute the probabilites.
        # Play with the same strategies as self.
        bjs = BlackJackSim(player_strategy = self._player_play_strategy, dealer_strategy = self._dealer_play_strategy)

        # if deck argument is provided, replace the trial BlackJackSim object's deck with it
        if (deck is not None): bjs.switch_deck(deck)
        
        for g in range(num_trials):

            msg = 'Probability trial: ' + str(g+1) # The +1 puts the counting for messaging on a 1...N basis instead of 0...N-1
            logger.debug(msg)
            
            # Clear the player and dealer hands in the simulation for this trial
            bjs.clear_hands()
        
            # Transfer dealer's cards to the dealer's hand in the simulation for this trial
            # TODO: Should not be directly using _dealer_hand when we are not self
            bjs._dealer_hand.add_cards(dealer_hand.get_cards())
            # If we got only one card from dealer_hand argument then draw the second
            # TODO: Should not be directly using _dealer_hand when we are not self
            if (bjs._dealer_hand.get_num_cards() == 1):
                bjs.draw_for_dealer()
                
            # Did the dealer draw to a blackjack?
            if (bjs.check_for_blackjack() != BlackJackCheck.DEALER_BLACKJACK ):
                
                # Dealer didn't draw to blackjack, so we need to run the trial...
            
                # Transfer player's cards to the player's hand in the simulation for this trial
                # TODO: Should not be directly using _player_hand when we are not self
                bjs._player_hand.add_cards(player_hand.get_cards())
        
                info = GamePlayOutcome()
        
                # Play the dealer's hand, and add hand outcome info to game info 
                dealer_info = bjs.play_dealer_hand()
                info.Dealer_Final_Hand = dealer_info.Final_Hand
                info.Dealer_Status = dealer_info.Status
                info.Dealer_Count = dealer_info.Count
        
                # First, we'll let the player stand
                player_hand_info = bjs.player_hand_info()
                info.Player_Final_Hand = player_hand_info.String_Rep
                info.Player_Status = BlackJackPlayStatus.STAND
                count_max = player_hand_info.Count_Max
                count_min = player_hand_info.Count_Min
                if (count_max <= 21):
                    info.Player_Count = count_max
                elif (count_min <= 21):
                    info.Player_Count = count_min
                else:
                    # TODO: Is this needed? Final logic should not let a BUST be the case, I think, since we haven't hit.
                    info.Player_Count = count_min
                    info.Player_Status = BlackJackPlayStatus.BUST
        
                # Deterimine game outcome after standing, and add to game info
                bjs.determine_game_outcome(info)
            
                msg = 'Probability trial: ' + str(g+1) + ' Stand Result: ' + str(info.Game_Outcome)
                logger.debug(msg)
                msg = 'Player Hand: ' + info.Player_Final_Hand + ' Dealer Hand: ' + info.Dealer_Final_Hand
                logger.debug(msg)

                # Accumulate proability information
                if info.Game_Outcome == BlackJackGameOutcome.PLAYER_WINS:
                    stand_win_count += 1
                elif info.Game_Outcome == BlackJackGameOutcome.PUSH:
                    stand_push_count += 1

                # Now we'll have the player hit
                bjs.draw_for_player()
                player_hand_info = bjs.player_hand_info()
                info.Player_Final_Hand = player_hand_info.String_Rep
                info.Player_Status = BlackJackPlayStatus.STAND
                count_max = player_hand_info.Count_Max
                count_min = player_hand_info.Count_Min
                if (count_max <= 21):
                    info.Player_Count = count_max
                elif (count_min <= 21):
                    info.Player_Count = count_min
                else:
                    info.Player_Count = count_min
                    info.Player_Status = BlackJackPlayStatus.BUST
        
                # Deterimine game outcome after hitting, and add to game info
                bjs.determine_game_outcome(info)
            
                msg = 'Probability trial: ' + str(g+1) + ' Hit Result: ' + str(info.Game_Outcome)
                logger.debug(msg)
                msg = 'Player Hand: ' + info.Player_Final_Hand + ' Dealer Hand: ' + info.Dealer_Final_Hand
                logger.debug(msg)
        
                # Accumulate proability information
                if info.Game_Outcome == BlackJackGameOutcome.PLAYER_WINS:
                    hit_win_count += 1
                elif info.Game_Outcome == BlackJackGameOutcome.PUSH:
                    hit_push_count += 1
                    
            else:
                # Dealer did draw to blackjack, so that means the player lost both hit and stand, and there was no push.
                # Log that dealer with a blackjack.
                msg = 'Probability trial: ' + str(g+1) + ' Dealer drew to blackjack and won.'
                logger.debug(msg)
                # TODO: Should not be directly using _dealer_hand when we are not self
                msg = 'Player Hand: ' + str(player_hand) + ' Dealer Hand: ' + str(bjs._dealer_hand)
                logger.debug(msg)
                
        # Compute probabilities
        hit_win_prob = hit_win_count / num_trials
        hit_push_prob = hit_push_count / num_trials
        stand_win_prob = stand_win_count / num_trials
        stand_push_prob = stand_push_count / num_trials

        return (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob)
    
    def percent_done(self, total, current):
        """
        This is a helper function used by, e.g., play_games() and play_batches_of_games(),to determine if and what percent d: one should be logged.
        The logic is that a percentage done will always be returned, but a boolean will also be returned if the percentage done is 10, 20, 30, ... 100,
        so that the calling method can choose to only occassionally report progress.
        :parameter total: The total number of, e.g., games or batches, to be played, int
        :parameter current: The current number of, e.g., game or batch being played, int
        :return: Tuple (report, percent_done)
            report = True if percent_done is 10, 20, 30, ... 100%, boolean
            percent_done = int(100 * current / total)
        """
        percent_done = 100.0 * current / total
        if current in [int(0.1*total) , int(0.2*total), int(0.3*total), int(0.4*total), int(0.5*total),
                       int(0.6*total), int(0.7*total), int(0.8*total), int(0.9*total)
                      ]:
            report = True
        else:
            report = False
        return (report, round(percent_done))
    