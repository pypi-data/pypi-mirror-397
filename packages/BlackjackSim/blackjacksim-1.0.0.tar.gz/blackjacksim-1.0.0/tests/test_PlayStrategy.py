# Standard
import unittest

# Local
from BlackjackSim.BlackJackSim import BlackJackSim
from BlackjackSim.PlayStrategy import PlayStrategy


class Test_PlayStrategy(unittest.TestCase):
    
    def test_split(self):
        ps = PlayStrategy()
        self.assertRaises(NotImplementedError, ps.split)

    def test_play(self):
        bjs = BlackJackSim()
        ps = PlayStrategy()
        self.assertRaises(NotImplementedError, ps.play, bjs.player_hand_info, bjs.draw_for_player, bjs.get_dealer_show)
        

if __name__ == '__main__':
    unittest.main()
