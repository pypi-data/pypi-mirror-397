"""
The functions in this module execute various use cases of the Blackjack game simulator. 

Exported Classes:
    None

Exported Exceptions:
    None
 
Exported Functions:
    simulate_blackjack_probability(...) - Runs simulations to determine how likeley it is to get Blackjack.
    play_interactive_probability() - Play an interactive game of Blackjack, but provide hit/stand and win/push probability info to user.
    play_interactive() - Play one interactive game of Blackjack.
    play_one_auto() - Automatically play one game of Blackjack, using Hoyle play strategy.
    play_many_auto() - Automatically play many games of Blackjack, using Hoyle play strategy, to generate game-play statistics.
    play_many_probabilities_auto() - Automatically play many games of Blackjack, using win/push probabilities to determine hit or stand.
    play_batches() - Automatically play many games of Blackjack in batches, using Hoyle play strategy. Answers question of
                     how much one might expect to lose after playing X games of Blackjack at a casino.
    __main__ -- Query user for a use case, and then call the appropriate function.
"""


# Standard imports
import logging
from pathlib import Path
from time import process_time
from random import seed

# Local imports
from HandsDecksCards.deck import StackedDeck, Deck
from HandsDecksCards.card import Card
from HandsDecksCards.hand import Hand
from BlackjackSim.BlackJackSim import BlackJackSim, GamePlayOutcome, BlackJackGameOutcome, BlackJackCheck
from BlackjackSim.PlayStrategy import InteractivePlayerPlayStrategy, InteractiveProbabilityPlayerPlayStrategy, ProbabilityPlayerPlayStrategy, CasinoDealerPlayStrategy, HoylePlayerPlayStrategy
from UserResponseCollector.UserQueryCommand import UserQueryCommandMenu, UserQueryCommandNumberInteger
from BlackjackSim.UserQueryCommandCards import UserQueryCommandCards
import UserResponseCollector.UserQueryReceiver


def play_debug_3():
    """
    Run a debugging scenario coded in this function.
    :return: None
    """
    seed(1234567890)
        
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    (results_list, net_expected) = sim.play_batches_of_games(10, 10)
        
    act_val = net_expected
        
    return None
  

def play_debug_2():
    """
    Run a debugging scenario coded in this function.
    :return: None
    """
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())

    dealer_hand = Hand()    
    dealer_hand.add_cards([Card('H','5')])
    player_hand = Hand()
    player_hand.add_cards([Card('S','A'),Card('C','5')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)
    
    return None


def play_debug():
    """
    Run a debugging scenario coded in this function.
    :return: None
    """
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    
    dealer_hand = Hand()    
    dealer_hand.add_cards([Card('D','2')])
    player_hand = Hand()
    player_hand.add_cards([Card('S','10'),Card('C','4')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)
     
    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','3')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','4')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','5')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','6')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','7')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','8')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','9')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','10')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)

    dealer_hand = Hand()
    dealer_hand.add_cards([Card('D','A')])
    (hit_win_prob, stand_win_prob, hit_push_prob, stand_push_prob) = sim.win_probability_hit_stand(player_hand,dealer_hand,1000)
    print(str(player_hand), ',', str(dealer_hand), ',', hit_win_prob, ',', stand_win_prob, ',', hit_push_prob, ',', stand_push_prob)


    #print('Hit Win Probability: ', hit_win_prob)
    #print('Hit Push Probability: ', hit_push_prob)
    #print('Stand Win Probability: ', stand_win_prob)
    #print('Stand Push Probability: ', stand_push_prob)
        
    return None


def simulate_blackjack_probability(num_deals = 10000):
    """
    Run simulations to determine how likely it is to get blackjack.
    :parameter num_deals: How many hands of Blackjack to play to generate probability results, int
    :return: None
    """
    # First, let's deal from an infinite deck
    
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    num_blackjacks = 0
    for deal in range(num_deals):
        sim.clear_hands()
        sim.draw_for_dealer(2)
        if (sim.check_for_blackjack() == BlackJackCheck.DEALER_BLACKJACK):
            num_blackjacks += 1
    
    # Expected blackjacks dealt from infinite deck = (16/52)*(4/52)+(4/52)*(16/52)
    # Or, conditional probability of getting a "10" card followed by an Ace +
    # conditional probability of getting an Ace followed by a "10" card.        
    print('% blackjacks dealt infintite deck (expected): ', 100.0*((16.0/52.0)*(4.0/52.0)+(4.0/52.0)*(16.0/52.0)))
    print('% blackjacks dealt  infinite deck (simulated): ', 100.0 * num_blackjacks / num_deals)
    
    # Next, let's deal from a normal 52 card deck
    
    d = Deck()
    sim.switch_deck(d)
    num_blackjacks = 0
    for deal in range(num_deals):
        d = Deck()
        sim.switch_deck(d)
        sim.clear_hands()
        sim.draw_for_dealer(2)
        if (sim.check_for_blackjack() == BlackJackCheck.DEALER_BLACKJACK):
            num_blackjacks += 1

    # Expected blackjacks dealt from non-infinite deck = (16/52)*(4/51)+(4/52)*(16/51)
    # Or, conditional probability of getting a "10" card followed by an Ace +
    # conditional probability of getting an Ace followed by a "10" card.        
    print('-----')
    print('% blackjacks dealt regular deck (expected): ', 100.0*((16.0/52.0)*(4.0/51.0)+(4.0/52.0)*(16.0/51.0)))
    print('% blackjacks dealt  regular deck (simulated): ', 100.0 * num_blackjacks / num_deals)

    return None


def play_interactive_probability():
    """
    Use BlackJackSim to play an interactive game, but provide hit/stand and win/push probability info to user.
    :return: None
    """
    sim = BlackJackSim(player_strategy = InteractiveProbabilityPlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    print('-------------------------------------------------------------------------')
    print('Starting an interactive game of blackjack with probability information...')
    print('-------------------------------------------------------------------------')
    info = sim.play_game()
    print('--------------------')
    print('     Winner:', info.Game_Outcome)
    print('     Player Status:', info.Player_Status)
    print('     Player Count:', info.Player_Count)
    print('     Player Hand:', info.Player_Final_Hand)
    print('     Dealer Status:', info.Dealer_Status)
    print('     Dealer Count:', info.Dealer_Count)
    print('     Dealer Hand:', info.Dealer_Final_Hand)
    if info.Split_Game_Outcome != BlackJackGameOutcome.NONE:
        # A pair was split. Provide output for the second player hand
        print('     Split Winner:', info.Split_Game_Outcome)
        print('     Split Status:', info.Split_Status)
        print('     Split Count:', info.Split_Count)
        print('     Split Hand:', info.Split_Final_Hand)

    return None


def play_interactive():
    """
    Use BlackJackSim to play an interactive game.
    :return: None
    """
    sim = BlackJackSim(player_strategy = InteractivePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    print('--------------------------------------------')
    print('Starting an interactive game of blackjack...')
    print('--------------------------------------------')
    info = sim.play_game()
    print('--------------------')
    print('     Winner:', info.Game_Outcome)
    print('     Player Status:', info.Player_Status)
    print('     Player Count:', info.Player_Count)
    print('     Player Hand:', info.Player_Final_Hand)
    print('     Dealer Status:', info.Dealer_Status)
    print('     Dealer Count:', info.Dealer_Count)
    print('     Dealer Hand:', info.Dealer_Final_Hand)
    if info.Split_Game_Outcome != BlackJackGameOutcome.NONE:
        # A pair was split. Provide output for the second player hand
        print('     Split Winner:', info.Split_Game_Outcome)
        print('     Split Status:', info.Split_Status)
        print('     Split Count:', info.Split_Count)
        print('     Split Hand:', info.Split_Final_Hand)

    return None


def play_one_auto():
    """
    Use BlackJackSim to play one game automatically, using Hoyle play strategy.
    :return: None
    """
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    print('-------------------------------')
    print('Starting a game of blackjack...')
    print('-------------------------------')
    info = sim.play_game()
    print('     Winner:', info.Game_Outcome)
    print('     Player Status:', info.Player_Status)
    print('     Player Count:', info.Player_Count)
    print('     Player Hand:', info.Player_Final_Hand)
    print('     Dealer Status:', info.Dealer_Status)
    print('     Dealer Count:', info.Dealer_Count)
    print('     Dealer Hand:', info.Dealer_Final_Hand)
    if info.Split_Game_Outcome != BlackJackGameOutcome.NONE:
        # A pair was split. Provide output for the second player hand
        print('     Split Winner:', info.Split_Game_Outcome)
        print('     Split Status:', info.Split_Status)
        print('     Split Count:', info.Split_Count)
        print('     Split Hand:', info.Split_Final_Hand)
        
    return None


def play_many_auto():
    """
    Use BlackJackSim to play a bunch of games automatically, using Hoyle play strategy.
    Example: Use this to see how often the player wins if they are dealt JH 9S, and dealer shows 7D.
    :return: None
    """

    # Get the hit/stand data logger so we can add a file handler to it if needed below
    logger = logging.getLogger('blackjack_logger.hit_stand_logger')

    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    # sim.set_player_play_strategy(CasinoDealerPlayStrategy())
    print('--------------------------------------------------------------------')
    print('Starting a bunch of games of blackjack to generate win statistics...')
    print('--------------------------------------------------------------------')
    
    # Ask if hit/stand data should be logged to file
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    query_preface = 'Do you want to log hit/stand data to file?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    fh = None # Because we need to have this variable in the outer scope
    if response == 'y':
            # TODO: Investigate if the generalization below will work on LINUX
            # We will always use the same log file name, placed in the user's Documents directory.
            home_path = Path().home().joinpath('Documents','hit_stand_training_data.log')
            fh = sim.setup_hit_stand_logging_file_handler(str(home_path))    

    # Ask how many games the user wants to have played
    # Build a query to ask how many games the user wants to have played
    query_preface = 'How many games do you want to automatically play?'
    command = UserQueryCommandNumberInteger(receiver, query_preface, minimum=1)
    num_games = command.Execute()
    
    # Ask if the user wants to specify the player's deal?
    player_deal = []
    player_init_hand = ''
    # Build a query to ask if the user wants to specify the player's deal
    query_preface = 'Do you want to specify the player''s deal?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    if response == 'y':
        # Build a query to get up to two cards from the user
        query_preface = 'Enter player deal of one or two cards.'
        command = UserQueryCommandCards(receiver, query_preface)
        player_deal = command.Execute()
    
        # Rebuild what should be the input string of cards provided by the user.
        # This will be printed in the output as proof that the user input has produced the desired result.
        for i in range(len(player_deal)):
            player_init_hand += str(player_deal[i]) + ' '
    
    # Ask if the user wants to specify the dealer's show card?    
    dealer_show = None
    # Build a query to ask if the user wants to specify the dealer's show card
    query_preface = 'Do you want to specify the dealer''s show card?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    if response == 'y':
        # Build a query to get one card from the user
        query_preface = 'Enter one dealer show card.'
        command = UserQueryCommandCards(receiver, query_preface)
        dealer_show = command.Execute()[0]

    # If you need repeatability, for example to debug something, then you can set a seed here.
    # from random import seed
    # seed(1234567890)

    print('--------------------')
    tic = process_time()
    info = sim.play_games(num_games, player_deal, dealer_show)
    toc = process_time()
    print('--------------------')
    print('Time to play games (s): ', (toc-tic))
    print('--------------------')
    
    dw = info.Dealer_Wins
    pw = info.Player_Wins
    pu = info.Pushes
    tg = dw + pw + pu
    dbj = info.Dealer_BlackJacks
    pbj = info.Player_BlackJacks
    
    print('     Dealer shows:', str(dealer_show))
    print('     Player initial hand:', player_init_hand)
    print('     Dealer Wins:', dw)
    print('     Player Wins:', pw)
    print('     Pushes:', pu)
    print('     Games Played:', tg)
    print('     Dealer % Wins:', ((100.0 * dw) / tg))
    print('     Player % Wins:', ((100.0 * pw) / tg))
    print('     Push %:', ((100.0 * pu) / tg))
    print('     Dealer BlackJacks:', dbj)
    print('     Player BlackJacks:', pbj)
    print('     Dealer % BlackJacks:', ((100.0 * dbj) / tg))
    print('     Player % BlackJacks:', ((100.0 * pbj) / tg))
    
    
    # Remove the file handler from the logger, if file handler was created.
    # This ensures that each time through this function in the same execution of __main__ that the user gets to
    # decide if logging to file should happen.
    if fh is not None:
        logger.removeHandler(fh)

    return None


def play_many_probabilities_auto():
    """
    Use BlackJackSim to play a bunch of games automatically.
    But using calculated probabilities of win/push to determine whether to hit or stand.
    Example: Use this to see how often the player wins if they are a savant and can compute probabilities in their head :)
    :return: None
    """

    # Get the hit/stand data logger so we can add a file handler to it if needed below
    logger = logging.getLogger('blackjack_logger.hit_stand_logger')

    sim = BlackJackSim(player_strategy = ProbabilityPlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    print('-------------------------------------------------------------------------------------------------------------------')
    print('Starting a bunch of games of blackjack to generate win statistics, and using win/push probabilities to hit/stand...')
    print('-------------------------------------------------------------------------------------------------------------------')
    
    # Ask if hit/stand data should be logged to file
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    query_preface = 'Do you want to log hit/stand data to file?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    fh = None # Because we need to have this variable in the outer scope
    if response == 'y':
            # TODO: Investigate if the generalization below will work on LINUX
            # We will always use the same log file name, placed in the user's Documents directory.
            home_path = Path().home().joinpath('Documents','hit_stand_training_data.log')
            fh = sim.setup_hit_stand_logging_file_handler(str(home_path))    

    # Ask how many games the user wants to have played
    # Build a query to ask how many games the user wants to have played
    query_preface = 'How many games do you want to automatically play?'
    command = UserQueryCommandNumberInteger(receiver, query_preface, minimum=1)
    num_games = command.Execute()
    
    # Ask if the user wants to specify the player's deal?
    player_deal = []
    player_init_hand = ''
    # Build a query to ask if the user wants to specify the player's deal
    query_preface = 'Do you want to specify the player''s deal?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    if response == 'y':
        # Build a query to get up to two cards from the user
        query_preface = 'Enter player deal of one or two cards.'
        command = UserQueryCommandCards(receiver, query_preface)
        player_deal = command.Execute()
    
        # Rebuild what should be the input string of cards provided by the user.
        # This will be printed in the output as proof that the user input as produced the desired result.
        for i in range(len(player_deal)):
            player_init_hand += str(player_deal[i]) + ' '
    
    # Ask if the user wants to specify the dealer's show card?    
    dealer_show = None
    # Build a query to ask if the user wants to specify the dealer's show card
    query_preface = 'Do you want to specify the dealer''s show card?'
    query_dic = {'y':'Yes', 'n':'No'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    if response == 'y':
        # Build a query to get one card from the user
        query_preface = 'Enter one dealer show card.'
        command = UserQueryCommandCards(receiver, query_preface)
        dealer_show = command.Execute()[0]

    # If you need repeatability, for example to debug something, then you can set a seed here.
    # seed(1234567890)

    tic = process_time()
    info = sim.play_games(num_games, player_deal, dealer_show)
    toc = process_time()
    print('--------------------')
    print('Time to play games (s): ', (toc-tic))
    print('--------------------')
    
    dw = info.Dealer_Wins
    pw = info.Player_Wins
    pu = info.Pushes
    tg = dw + pw + pu
    dbj = info.Dealer_BlackJacks
    pbj = info.Player_BlackJacks
    
    print('     Dealer shows:', str(dealer_show))
    print('     Player initial hand:', player_init_hand)
    print('     Dealer Wins:', dw)
    print('     Player Wins:', pw)
    print('     Pushes:', pu)
    print('     Games Played:', tg)
    print('     Dealer % Wins:', ((100.0 * dw) / tg))
    print('     Player % Wins:', ((100.0 * pw) / tg))
    print('     Push %:', ((100.0 * pu) / tg))
    print('     Dealer BlackJacks:', dbj)
    print('     Player BlackJacks:', pbj)
    print('     Dealer % BlackJacks:', ((100.0 * dbj) / tg))
    print('     Player % BlackJacks:', ((100.0 * pbj) / tg))
    
    
    # Remove the file handler from the logger, if file handler was created.
    # This ensures that each time through this function in the same execution of __main__ that the user gets to
    # decide if logging to file should happen.
    if fh is not None:
        logger.removeHandler(fh)

    return None    


def play_batches():
    """
    Use BlackJackSim to play a bunch of batches of games automatically.
    Example: Use this to see the distibution of net wins if you play 20 hands of blackjack many times.
    :return: None
    """
    sim = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    print('---------------------------------------------------------------------------------------')
    print('Playing batches of blackjack games to determine distribution of net wins for a batch...')
    print('---------------------------------------------------------------------------------------')
    
    # Ask how many games the user wants to have played in each batch
    # Build a query to ask how many games the user wants to have played in each batch
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    query_preface = 'How many games per batch do you want to automatically play?'
    command = UserQueryCommandNumberInteger(receiver, query_preface, minimum=1)
    num_games = command.Execute()
    
    # Ask how many batches the user wants to have played
    # Build a query to ask how many batches the user wants to have played
    query_preface = 'How many batches do you want to automatically play?'
    command = UserQueryCommandNumberInteger(receiver, query_preface, minimum=1)
    num_batches = command.Execute()
    
    # If you need repeatability, for example to debug something, then you can set a seed here.
    # seed(1234567890)

    tic = process_time()
    (results_list, net_expected, batch_stats) = sim.play_batches_of_games(num_games, num_batches)
    toc = process_time()
    print('--------------------')
    print('Time to play batches of games (s): ', (toc-tic))
    print('--------------------')
    
    for tup in results_list:
        print('net wins: ', tup[0], 'number of times: ', tup[1], 'fraction of times: ', tup[2])
    print('expected value for net wins: ', net_expected)

    print('--------------------')
    print('mean player win %: ', batch_stats.Player_Win_Percent_Mean)
    print('player win % standard error: ', batch_stats.Player_Win_Percent_StdErr)
    print('mean dealer win %: ', batch_stats.Dealer_Win_Percent_Mean)
    print('dealer win % standard error: ', batch_stats.Dealer_Win_Percent_StdErr)
    print('push %: ', batch_stats.Push_Percent_Mean)
    print('push % standard error: ', batch_stats.Push_Percent_StdErr)
    print('mean player blackjack %: ', batch_stats.Player_BlackJack_Percent_Mean)
    print('player blackjack % standard error: ', batch_stats.Player_BlackJack_Percent_StdErr)
    print('mean dealer blackjack %: ', batch_stats.Dealer_BlackJack_Percent_Mean)
    print('dealer blackjack % standard error: ', batch_stats.Dealer_BlackJack_Percent_StdErr)

    return None



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    
    """
    Query the user for how they wish to use the BlackJack simulator, and then launch that usage.
    This includes a "debug" usage to set up what ever situation is needed for debugging, since I can't seem to reliably debug unit tests.
    """
    
    # Set up logging
    BlackJackSim().setup_logging()
    
    print('--------------------')
    print('*** Python Blackjack Simulator ***')
    print('--------------------')
        
    # Build a query for the user to obtain their choice of how to user the simulator
    receiver = UserResponseCollector.UserQueryReceiver.UserQueryReceiver_GetCommandReceiver()
    query_preface = 'How do you want to use the simulator?'
    query_dic = {'q':'Quit', 'i':'Interactive Game', 'p':'Interactive Game with Probabilities', 'a':'Automatic Game', 'm':'Many Automatic Games', 'u':'Many Automatic Games Using Probabilities'   , 'b':'Batches of Games', 'j':'Blackjack Probability', 'd':'Debug Scenario'}
    command = UserQueryCommandMenu(receiver, query_preface, query_dic)
    response = command.Execute()
    
    while response != 'q':
        
        match response:
            
            case 'i':
                play_interactive()
                
            case 'a':
                play_one_auto()
                
            case 'm':
                play_many_auto()
                
            case 'b':
                play_batches()
                
            case 'p':
                play_interactive_probability()
                
            case 'u':
                play_many_probabilities_auto()
                
            case 'j':
                simulate_blackjack_probability()
                
            case 'd':
                play_debug_3()
                
        
        print('--------------------')
        response = command.Execute()
      
    # *** Use BlackJackSim to play a game with a stacked deck to produce a desired outcome ***

    # bjs = BlackJackSim(player_strategy = HoylePlayerPlayStrategy(), dealer_strategy = CasinoDealerPlayStrategy())
    # print('Starting a game of black jack with a stacked deck to have player and dealer get blackjack...')
        
    # # Replace sim's deck with StackedDeck
    # # Create a StackedDeck
    # sd = StackedDeck()
    # # It's assumed that BlackJackSim.play_game() will give first two cards in deck to dealer.
    # sd.add_cards([Card('C','A'), Card('D','K'), Card('S','10'), Card('H','A')])
    # # Replace sim's deck with the StackedDeck
    # bjs.switch_deck(sd)
       
    # info = bjs.play_game()
    # print('     Winner:', info.Game_Outcome)
    # print('     Player Status:', info.Player_Status)
    # print('     Player Count:', info.Player_Count)
    # print('     Player Hand:', info.Player_Final_Hand)
    # print('     Dealer Status:', info.Dealer_Status)
    # print('     Dealer Count:', info.Dealer_Count)
    # print('     Dealer Hand:', info.Dealer_Final_Hand)
    # if info.Split_Game_Out != BlackJackGameOutcome.NONE:
    #     # A pair was split. Provide output for the second player hand
    #     print('     Winner:', info.Split_Game_Outcome)
    #     print('     Split Status:', info.Split_Status)
    #     print('     Split Count:', info.Split_Count)
    #     print('     Split Hand:', info.Split_Final_Hand)