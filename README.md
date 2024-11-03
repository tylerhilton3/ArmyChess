# Overview

This is a simple chess game that can be played with 2 players on the same device, or between 2 devices online.

[Software Demo Video](https://youtu.be/zEx3Skc4JRc)

### Single player

It includes all formal chess rules, like en passant, castling, stalemate, etc. I added sound effects, an end screen, and a 5 minute timer for each player. You can play now by running singleplayer/game.py

### Multiplayer

Right now, the multiplayer version is not playable publicly because it is connected to my own private Firebase Realtime Database, which doesn't yet have authentication. I've gitignore'd client/firebaseprivatekey.json and setup the cred variable in client/client.py to access my current database, but if you link your own database by updating those corresponding files, it will all work perfectly.

The first person to connect to the database will be white, the second player to connect will be black. I've set it up to allow multiple games to be played simultaneously.

# Network Communication

I used peer-to-peer communication methods over an online database. Each client has listeners for updates in specific nodes.

# Development Environment

I used Python as the programming language and pygame as the game engine library. I used Firebase's Realtime Database to store the board state and game variables. I used system libraries like sys and os to manage file dependencies, and the firebase_admin library to interact with the database.

# Future Work/Bugfixes

- **Silent Opponent Moves**  
  Currently, the opponent's moves are made without any sound effect.

- **Illegal Moves Switching Turn**  
  When an illegal move is attempted, the turn sometimes switches erroneously, potentially allowing the king to be captured if in check.

- **Inverse Capture Circles**  
  Capture indicators are displayed on incorrect squares, inverting the intended location relative to the pieces.

- **Occasional Checkmate Failures**  
  In some scenarios, checkmate is not correctly recognized, allowing the game to continue.