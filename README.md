# Puzzle Game

A 2D puzzle game built with Python and Pygame. The player moves a sprite in four directions through a series of rooms. Solving each room's puzzle opens the door to the next room, until the player reaches victory.

Capstone project (CMSC 495), University of Maryland Global Campus. Built by a team of four. (Spring, 2026)

## My contribution

- Designed the puzzles and room layouts
- Coded the puzzles into the game
- Tested the code
- Used Git and GitHub with my teammates for version control

## How to play

- WASD or Arrow keys for movement
- Spacebar to interact
- Mouse Click on relevant buttons (Start, Resume, Pause, Leaderboard)
- Solve the puzzle in each room to open the door to the next. Reach the final room to win.

## Run it

Requires Python 3 and Pygame.

```bash
pip install pygame
python main.py
```

## Project structure

The project is organized into Python modules for game execution, menus, puzzle rooms, gameplay mechanics, and supporting utilities. The assets/ directory contains game resources.

Puzzle-Game/
├── assets/
├── main.py
├── menus.py
├── leaderboard.py
├── layout_algorithim.py
├── start_room.py
├── win_room.py
├── HiddenPathRoom.py
├── LavaRoom.py
├── NoBacktrackRoom.py
├── MemoryPathRoom.py
├── FrictionlessFloor.py
├── simon_says.py
├── switch_grid.py
├── swapbuckets.py
└── teleportation.py

Core Game Files

main.py — Main entry point for the game. Likely initializes Pygame, manages the main game loop, handles player input, and coordinates transitions between rooms.
menus.py — Handles the game's menus and user interface, including navigation and menu buttons such as Start, Resume, and Pause.
leaderboard.py — Manages the leaderboard and displays player scores.
layout_algorithim.py — Contains logic for randomly arranges the premade rooms.
start_room.py — Defines the starting room and its initial gameplay setup.
win_room.py — Defines the final room or victory state displayed when the player completes the game.

Puzzle Rooms and Mechanics

HiddenPathRoom.py — Implements a puzzle room in which the player must discover or navigate a hidden path.
LavaRoom.py — Implements a room featuring lava hazards that the player must avoid to progress.
NoBacktrackRoom.py — Implements a puzzle that challenges the player to navigate without retracing previously visited steps.
MemoryPathRoom.py — Implements a memory-based path puzzle in which the player must remember a sequence or route.
FrictionlessFloor.py — Implements a movement puzzle in which the player slides across a frictionless or low-friction surface.
simon_says.py — Implements a Simon Says-style memory puzzle that challenges the player to repeat a sequence of sounds.
switch_grid.py — Implements a grid-based puzzle involving switches that the player must activate to complete a portrait.
swapbuckets.py — Implements a bucket-swapping puzzle that requires the player to choose the correct bucket.
teleportation.py — Implements teleportation mechanics in a puzzle involving movement between locations.

Assets

assets/ — Contains game resources, such as sprites, images, backgrounds, fonts, sound effects, or other files used by the game.

## Team

Team of Four

## Author

Samrat Shakya
