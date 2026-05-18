# **🧮Connect Four AI - README**
**Overview**
This is a Connect Four game implementation with multiple AI opponents using different search algorithms. The game features a graphical user interface built with Pygame, allowing players to compete against AI agents that use various decision-making strategies.

**Features**
- Interactive GUI with color selection for game pieces

- Three AI Algorithms to play against:

1. Minimax

2. Alpha-Beta Pruning

3. Expected Minimax (with probabilistic outcomes)

- Adjustable Search Depth (K) - control how many moves ahead the AI looks

- Tree Visualization - shows the AI's decision tree during gameplay

- Performance Metrics - displays nodes expanded and computation time for each AI move

- Final Scoring - counts the number of 4-in-a-row connections for both players

*Game Rules*
Connect Four is a two-player connection game where players take turns dropping colored discs into a vertically suspended grid (6 rows × 7 columns). The first player to form a horizontal, vertical, or diagonal line of four discs wins.

## AI Algorithms
1. Minimax
- Classic recursive search algorithm

- Evaluates all possible moves up to depth K

- Returns the move that maximizes AI's score while minimizing player's potential

2. Alpha-Beta Pruning
- Optimization of Minimax

- Prunes branches that cannot influence the final decision

- Significantly reduces the number of nodes evaluated

3. Expected Minimax
- Handles probabilistic outcomes (simulates imperfect control)

- When AI intends to drop in column c, there's a 60% chance it lands there, and 20% chance each for adjacent columns

- Useful for modeling realistic scenarios with execution uncertainty

**Heuristic Function**
The AI evaluates board positions using a weighted scoring system:

|Feature	|AI Value	|Player Value|
|Center column control	|+3 per disc|- |
|2-in-a-row windows	+2|	|-2|
|3-in-a-row windows	+6	|-8|
|4-in-a-row windows (win)	|+100	|-120|
|Potential windows (no opponent)|	+1 each	|-1 each|

```
### File Structure
connect-four-ai/
├── game.py           # Core game logic, board operations, win detection
├── ai.py             # AI algorithms, heuristic evaluation, move ordering
└── gui_pygame.py     # Pygame GUI, event handling, visualization
