# cs32-final-project
CS32 final project

## Overview

BY: Tyler Ory and Ann Nguyen

This project is a python-based reimagining of the classic Flappy Bird game. 
The player controls a bird represented by a single character (`*`) and must navigate through a series of pipes that move across the screen. 

The game includes:
- Four difficulty modes: Easy, Medium, Hard, and Endless.
- Increasing difficulty in Endless mode (pipes get faster and narrower).
- Per-mode high score tracking, stored in a JSON file.
- An ASCII-art intro and an animated loading bar.
- Smooth character physics using gravity and jumping mechanics.

This project demonstrates object-oriented programming, real-time input handling, and text-based UI rendering in the terminal.

## Features

- ✅ Multiple difficulty levels with unique mechanics:
  - Easy: Wide pipe spacing and slower timestep.
  - Medium: Standard settings.
  - Hard: Fast pipes, shrinking gaps, and faster timestep.
  - Endless: Starts like Easy and gradually gets harder.
- ✅ Dynamic gameplay (increasing challenge in real time).
- ✅ JSON-based high score persistence for each mode.
- ✅ ASCII intro screen and loading animation.
- ✅ In-terminal real-time rendering and physics.

## Use of Generative AI
I used generative AI (ChatGPT) as a coding assistant during this project in the following ways:

Real-time input handling: I asked for help implementing real-time keypress handling for gameplay, specifically using low-level terminal control (e.g., termios, tty, select) to allow smooth jumping and menu navigation.

Code cleanup and simplification: I used AI to help reorganize and refactor parts of my code to be more readable and modular

Gameplay structure: While I designed the game concept and mechanics myself, I consulted AI for guidance on structuring the main game loop, collision detection, and score handling

## How to Run

** The game runs best on a local machine. Download the file to your computer and ideally run it on VSCode **

- After launching the program, you’ll see a title screen followed by a main menu where you can select between Easy, Medium, Hard, or Endless mode.
- To start the game, use your keyboard to press the number corresponding to the desired difficulty.
- During gameplay, your bird (represented by *) will automatically fall due to gravity.
- Press the spacebar to make the bird jump upward.
- Your goal is to fly through gaps in the pipes and survive as long as possible without crashing into the pipes.
- You gain one point for every set of pipes you successfully pass through.
- The game ends when the bird collides with a pipe
- At the end of each game, you'll see your score, the high score for that difficulty, and an option to play again, return to the main menu, or exit.
- High scores are saved per mode and persist across sessions.

### Instructions

1. Clone or download this repository.
2. Open a terminal and navigate to the project directory.
3. Run the game with:

   ```bash
   python3 flappy.py
