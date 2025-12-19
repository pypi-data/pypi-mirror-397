# BlackjackSim

Source code: [GitHub](https://github.com/KevinRGeurts/BlackjackSim)
---
BlackjackSim is a Python implementation of the Blackjack card game. It allows interactive play with one player and a computer dealer.
It also includes a simulation mode where both the dealer and the player are played by the computer. Simulation mode can be used
to analyze different player strategies over many hands, and to generate game-play statistics. In simulation mode, the player uses
a play strategy described by Hoyle's Rules of Games.

## Credit where credit is due

- The Strategy design pattern is used to implement playing strategies, and follows the concepts, UML diagrams, and examples provided in
  "Design Patterns: Elements of Reusable Object-Oriented Software," by Eric Gamma, Richard Helm, Ralph Johnson,
  and John Vlissides, published by Addison-Wesley, 1995.
- The ```HoylePlayerPlayStrategy``` class implements the player strategy as described in "Hoyle's Rules of Games," by A.H. Morehead and G. Mott-Smith, second revised edition, published by Signet, 1983.

## Requirements
- UserResponseCollector>=1.0.4: [GitHub](https://github.com/KevinRGeurts/UserResponseCollector), [PyPi](https://pypi.org/project/UserResponseCollector/)
- HandsDecksCards>=1.0.0: [GitHub](https://github.com/KevinRGeurts/HandsDecksCards), [PyPi](https://pypi.org/project/HandsDecksCards/)

## Usage
To play the game interactively or to run various simulations:
```
python -m BlackjackSim.main
```
A menu of options for play and simulation will be presented.

## Unittests
Unit tests for BlackJackSim have filenames starting with test_. To run the unit tests,
type ```python -m unittest discover -s .\..\tests -v``` in a terminal window in the project directory.

## License
MIT License. See the LICENSE file for details