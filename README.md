# Rock-Paper-Scissors
TCP based Rock-Paper-Scissors multiplayer game

## Objective
A multiplayer game to demonstrate exchange of packets between server and client

## Description
1. The game follows three simple rule:
- Rock breaks scissors
- Paper wraps rock
- Scissors cut paper

2. Each player (or client) sends a packet with a command which tells the server what to execute

3. Following actions are available for the players
  - Create or join a game
  - Play a move and wait for the server to calculate the winner
  - Rematch or leave the game

4. The server can handle multiple games at a time and also destroys a game when all players leave

## Installation and Usage
  1. Clone this repository and install requirements from Pipfile
  2. Run ```server.py```
  3. Run ```player.py``` multiple times in new terminal windows, one for each player
  4. Create or join a game to play and follow onscreen instructions
  
### Note: Game is WIP
