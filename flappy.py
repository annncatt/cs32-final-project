import random
import time
import os
import sys
import termios
import tty
import select
import json

# Constants
SCREEN_HEIGHT = 20
SCREEN_WIDTH = 70
pipe_cap_def = '==='
pipe_cap = '='
pipe_side = '|'
pipe_middle = ' '
pipe_width = len(pipe_cap_def)
max_height = 11
min_height = 3
GAP_HEIGHT = 8
PIPE_SPACING = 16
TIME_STEP = 0.08 #0.12  # Smoother updates
GAME_TIME = 60
BIRD_CHAR = '*'
GRAVITY = 9.8*1.45 #1.35  # pixels/sec^2
JUMP_STRENGTH = -9.5  # pixels/sec
bird_x = SCREEN_WIDTH // 4
HIGHSCORE_FILE = "highscore.json"
default_high_scores = {
    "easy": 0,
    "medium": 0,
    "hard": 0,
    "endless": 0
}

# Terminal input setup
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

# Pipe class
class Pipe:
    def __init__(self, x_position):
        self.bottom_height = random.randint(min_height, max_height)
        self.gap = GAP_HEIGHT
        self.top_height = SCREEN_HEIGHT - self.bottom_height - self.gap - 2
        self.x = x_position
        self.width = pipe_width
        self.scored = False

    def move(self):
        self.x -= 1

    def get_visible_columns(self):
        columns = []
        for i in range(pipe_width):
            global_x = self.x + i
            if 0 <= global_x < SCREEN_WIDTH:
                col = [' '] * SCREEN_HEIGHT
                bottom_start = SCREEN_HEIGHT - self.bottom_height - 1
                for y in range(bottom_start, SCREEN_HEIGHT - 1):
                    col[y] = pipe_side if i in (0, 2) else pipe_middle
                if bottom_start - 1 >= 1:
                    col[bottom_start - 1] = pipe_cap
                top_end = self.top_height + 1
                for y in range(0, top_end + 1):
                    col[y] = pipe_side if i in (0, 2) else pipe_middle
                if top_end < SCREEN_HEIGHT - 1:
                    col[top_end] = pipe_cap
                columns.append((global_x, col))
        return columns

#### Load high scores
def save_high_score(score, mode):
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = default_high_scores.copy()

    data[mode] = max(score, data.get(mode, 0))

    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(data, f)

def load_all_high_scores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            return json.load(f)
    return default_high_scores.copy()

def get_best_high_score():
    scores = load_all_high_scores()
    best_mode = max(scores, key=scores.get)
    return scores[best_mode], best_mode


# Utility functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_empty_screen():
    screen = ['#' * SCREEN_WIDTH]
    for _ in range(SCREEN_HEIGHT - 2):
        screen.append('#' + ' ' * (SCREEN_WIDTH - 2) + '#')
    screen.append('#' * SCREEN_WIDTH)
    return screen

def draw_pipe_on_screen(screen, pipe):
    screen_chars = [list(row) for row in screen]
    pipe_columns = pipe.get_visible_columns()
    for x, col in pipe_columns:
        for y in range(SCREEN_HEIGHT):
            if 0 <= y + 1 < SCREEN_HEIGHT - 1:
                screen_chars[y + 1][x] = col[y]
    return [''.join(row) for row in screen_chars]

def kbhit():
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    return dr != []

# Screens
def intro_screen():
    clear()
    art = [
        "  ______ _                    _  ____  _  ____        _ ",
        " |  ____| |                  (_)|    )(_)|    \      | |",
        " | |__  | | __ _ _ __ _ _ __  _ | () / _ | () |    __| |",
        " |  __| | |/ _` | '_  \| '_ \| ||   | | ||  _ \  /  _| |",
        " | |    | | (_| | |_) || |_) | || () \| || | \ \ | (_| |",
        " |_|    |_|\___,|_.__/_| .__/|_||____)|_||_|  |_|\__,|_|",
        "                | |    | |                              ",
        "                |_|    |_|                              "
    ]
    pad = (SCREEN_WIDTH - len(art[0])) // 2
    screen = create_empty_screen()
    for i, line in enumerate(art):
        if 2 + i < SCREEN_HEIGHT - 1:
            screen[2 + i] = '#' + ' ' * pad + line + ' ' * (SCREEN_WIDTH - 2 - pad - len(line)) + '#'

    # Print art
    for line in screen:
        print(line)

    # Loading bar
    bar_length = 30
    load_time = 3  # seconds
    step_delay = load_time / bar_length
    prefix = " " * ((SCREEN_WIDTH - (bar_length + 10)) // 2) + "Loading: "

    for i in range(1, bar_length - 1):
        filled = "█" * i
        unfilled = " " * (bar_length - 2 - i)
        print(f"\r{prefix}[{filled}{unfilled}]", end='', flush=True)
        time.sleep(step_delay)

    input("\n\nPress Enter to continue...")

def main_menu():
    clear()
    print("\n" * 2)
    print(" " * 20 + "Flappy Bird Main Menu")
    best_score, best_mode = get_best_high_score()
    if best_score > 0:
        print(" " * 20 + f"High Score: {best_score} ({best_mode.capitalize()} Mode)")
    else:
        print(" " * 20 + "High Score: 0")
    print("\n" * 1)
    print(" " * 20 + "1. Easy Mode")
    print(" " * 20 + "2. Medium Mode")
    print(" " * 20 + "3. Hard Mode")
    print(" " * 20 + "4. Endless Mode")
    print(" " * 20 + "5. Exit")
    print("\n" * 2)
    tty.setcbreak(fd)
    while True:
        choice = sys.stdin.read(1)
        if choice in ['1', '2', '3', '4', '5']:
            return choice

def game_over_screen(score):
    high_score = load_high_score()
    clear()
    print("\n" * 2)
    print(" " * 25 + "##### GAME OVER #####")
    print(f" " * 25 + f"Your score: {score}")
    print(" " * 25 + f"High Score: {high_score}")
    print("\n")
    print(" " * 25 + "1. Play Again")
    print(" " * 25 + "2. Return to Menu")
    print(" " * 25 + "3. Exit")
    tty.setcbreak(fd)
    while True:
        choice = sys.stdin.read(1)
        if choice in ['1', '2', '3']:
            return choice

# Main game loop
def run_game(config):
    pipes = [Pipe(x_position=SCREEN_WIDTH)]
    start_time = time.time()
    bird_y = float(SCREEN_HEIGHT // 2)
    bird_velocity = 0.0
    score = 0

    gap_height = GAP_HEIGHT
    min_gap_height = 4
    last_gap_update = time.time()
    gap_shrink_interval = 10  # seconds

    # Unpack config
    time_step = config['TIME_STEP']
    gravity = config['GRAVITY']
    pipe_spacing = config['PIPE_SPACING']
    dynamic_gap = config['DYNAMIC_GAP_SHIFT']
    endless = config['ENDLESS']
    dynamic_gap_enabled = dynamic_gap  # for hard mode; for endless, will change later

    try:
        while True:
            # Adjust difficulty over time for endless mode
            if endless:
                elapsed = time.time() - start_time
                pipe_spacing = min(20, 32 - int(elapsed // 10))
                time_step = max(0.06, config['TIME_STEP'] - 0.005 * (elapsed // 15))
                gravity = min(9.8 * 1.6, config['GRAVITY'] + 0.2 * (elapsed // 15))
                if elapsed > 45:
                    dynamic_gap_enabled = True

            # Shrink pipe gap over time (for hard or endless)
            if config['SHRINK_GAP'] and time.time() - last_gap_update > gap_shrink_interval:
                if config['ENDLESS']:
                    # Only shrink for first 45 seconds in endless
                    if elapsed <= 45 and gap_height > min_gap_height:
                        gap_height -= 1
                        last_gap_update = time.time()
                else:
                    # Always shrink in hard mode
                    if gap_height > min_gap_height:
                        gap_height -= 1
                        last_gap_update = time.time()

            # Physics
            bird_velocity += gravity * time_step
            bird_y += bird_velocity * time_step
            bird_y = max(1, min(SCREEN_HEIGHT - 2, bird_y))

            # Input
            if kbhit():
                ch = sys.stdin.read(1)
                if ch == ' ':
                    bird_velocity = JUMP_STRENGTH

            # Pipes
            for pipe in pipes:
                pipe.move()
            for pipe in pipes:
                if not pipe.scored and pipe.x + pipe.width < bird_x:
                    score += 1
                    pipe.scored = True
            pipes = [p for p in pipes if p.x + pipe.width > 0]

            if not pipes or pipes[-1].x <= SCREEN_WIDTH - pipe_spacing - pipe_width:
                new_pipe = Pipe(x_position=SCREEN_WIDTH)
                new_pipe.gap = gap_height
                new_pipe.top_height = SCREEN_HEIGHT - new_pipe.bottom_height - new_pipe.gap - 2
                pipes.append(new_pipe)

            # Render
            screen = create_empty_screen()
            for pipe in pipes:
                screen = draw_pipe_on_screen(screen, pipe)
            screen_chars = [list(row) for row in screen]
            screen_chars[int(bird_y)][bird_x] = BIRD_CHAR
            screen = [''.join(row) for row in screen_chars]

            score_panel = [
                "#############",
                f"# SCORE: {score:<3}#",
                "#############"

            ]
            while len(score_panel) < SCREEN_HEIGHT:
                score_panel.append(' ' * len(score_panel[0]))
            combined_screen = [
                screen[i] + ' ' + score_panel[i] for i in range(SCREEN_HEIGHT)
            ]

            # Collision detection
            for pipe in pipes:
                if pipe.x <= bird_x <= pipe.x + pipe.width - 1:
                    for (x, col) in pipe.get_visible_columns():
                        if x == bird_x:
                            y = int(bird_y) - 1
                            if 0 <= y < SCREEN_HEIGHT:
                                if col[y] in (pipe_side, pipe_cap):
                                    time.sleep(time_step * 10)
                                    return score

            clear()
            for line in combined_screen:
                print(line)
            time.sleep(time_step)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return score


easy_config = {
    'TIME_STEP': 0.10,
    'GRAVITY': 9.8 * 1.2,
    'PIPE_SPACING': 32,
    'DYNAMIC_GAP_SHIFT': False,
    'ENDLESS': False,
    'SHRINK_GAP': False
}

medium_config = {
    'TIME_STEP': 0.08,
    'GRAVITY': 9.8 * 1.45,
    'PIPE_SPACING': 24,
    'DYNAMIC_GAP_SHIFT': False,
    'ENDLESS': False,
    'SHRINK_GAP': False
}

hard_config = {
    'TIME_STEP': 0.06,
    'GRAVITY': 9.8 * 1.6,
    'PIPE_SPACING': 20,
    'DYNAMIC_GAP_SHIFT': True,
    'ENDLESS': False,
    'SHRINK_GAP': True
}

endless_config = {
    'TIME_STEP': 0.10,
    'GRAVITY': 9.8 * 1.2,
    'PIPE_SPACING': 32,
    'DYNAMIC_GAP_SHIFT': False,
    'ENDLESS': True,
    'SHRINK_GAP': True
}

def run_game_with_retries(config, mode):
    while True:
        score = run_game(config)
        save_high_score(score, mode)

        next_choice = game_over_screen(score, mode)
        if next_choice == '3':
            sys.exit(0)
        elif next_choice == '2':
            break
        elif next_choice == '1':
            continue

def game_over_screen(score, mode):
    scores = load_all_high_scores()
    high_score = scores.get(mode, 0)

    clear()
    print("\n" * 2)
    print(" " * 25 + "##### GAME OVER #####")
    print(f" " * 25 + f"Your score: {score}")
    if high_score > 0:
        print(f" " * 25 + f"High Score ({mode.capitalize()}): {high_score}")
    print("\n")
    print(" " * 25 + "1. Play Again")
    print(" " * 25 + "2. Return to Menu")
    print(" " * 25 + "3. Exit")
    tty.setcbreak(fd)
    while True:
        choice = sys.stdin.read(1)
        if choice in ['1', '2', '3']:
            return choice


# ------------------ GAME START ------------------
if __name__ == '__main__':
    try:
        tty.setcbreak(fd)
        intro_screen()
        while True:
            choice = main_menu()
            if choice == '1':
                run_game_with_retries(easy_config, 'easy')
            elif choice == '2':
                run_game_with_retries(medium_config, 'medium')
            elif choice == '3':
                run_game_with_retries(hard_config, 'hard')
            elif choice == '4':
                run_game_with_retries(endless_config, 'endless')

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
