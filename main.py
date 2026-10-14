# comments in python start with a hash instead of //
# pylint: disable=no-member
import pygame
import sys
from datetime import datetime
import random
pygame.init()
# ======================
# CONSTANTS
# ======================
TILE_SIZE = 64
SCREEN_WIDTH = 16 * TILE_SIZE
SCREEN_HEIGHT = 12 * TILE_SIZE
SPEED = 8
GRID_COLS = SCREEN_WIDTH // TILE_SIZE  # 16
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE  # 12
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.init()
clock = pygame.time.Clock()
# ======================
# game files
# ======================
import start_room
import win_room
import simon_says
import FrictionlessFloor
import teleportation
import switch_grid
import LavaRoom
import MemoryPathRoom
import NoBacktrackRoom
import HiddenPathRoom
import swapbuckets
games = [simon_says, FrictionlessFloor, teleportation, switch_grid, LavaRoom, MemoryPathRoom, NoBacktrackRoom, HiddenPathRoom, swapbuckets]

from menus import MenuManager
from leaderboard import LeaderboardManager

# ===========================
# game information
# ===========================
pygame.display.set_caption("start room")
menu = MenuManager(screen)
lb = LeaderboardManager(screen)
d0 = datetime(2008, 8, 18)
d1 = datetime.now()
delta = d1 - d0
random.seed(delta.days)
# ======================
# ASSETS
# ======================
def load_img(path, alpha=False):
    img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

# Door assets  — Left tile = the tile closer to col 0 / row 0 of the pair
door_imgs = {
    "west_left_open": load_img('assets/WestLeftDoorOpen.png', alpha=True),
    "west_right_open": load_img('assets/WestRightDoorOpen.png', alpha=True),
    "west_left_closed": load_img('assets/WestLeftDoorClosed.png', alpha=True),
    "west_right_closed": load_img('assets/WestRightDoorClosed.png', alpha=True),
    "east_left_open": load_img('assets/EastLeftDoorOpen.png', alpha=True),
    "east_right_open": load_img('assets/EastRightDoorOpen.png', alpha=True),
    "east_left_closed": load_img('assets/EastLeftDoorClosed.png', alpha=True),
    "east_right_closed": load_img('assets/EastRightDoorClosed.png', alpha=True),
    "north_left_open": load_img('assets/NorthLeftDoorOpen.png', alpha=True),
    "north_right_open": load_img('assets/NorthRightDoorOpen.png', alpha=True),
    "north_left_closed": load_img('assets/NorthLeftDoorClosed.png', alpha=True),
    "north_right_closed": load_img('assets/NorthRightDoorClosed.png', alpha=True),
    "south_left_open": load_img('assets/SouthLeftDoorOpen.png', alpha=True),
    "south_right_open": load_img('assets/SouthRightDoorOpen.png', alpha=True),
    "south_left_closed": load_img('assets/SouthLeftDoorClosed.png', alpha=True),
    "south_right_closed": load_img('assets/SouthRightDoorClosed.png', alpha=True),
}
wall_img = load_img('assets/Wall1.png')  # wall border
floor_img = load_img('assets/Path2.png')  # safe / normal floor
ice_img = load_img('assets/IceFloor.png', alpha=True)  # slippery ice
rock_img = load_img('assets/Rock.png', alpha=True)

#pause_btn_img = pygame.image.load('assets/PauseButton.png').convert_alpha()  # Pause button
#pause_btn_img = pygame.transform.scale(pause_btn_img, (48, 48))

# Player sprites
player_imgs = {
    "down": load_img('assets/Char1-1.png'),
    "right": load_img('assets/Char1-2.png'),
    "up": load_img('assets/Char1-3.png'),
    "left": load_img('assets/Char1-4.png'),
}
for img in player_imgs.values():
    img.set_colorkey((0, 0, 0))
movinggus = player_imgs["down"]
# Tile images
font = pygame.font.Font(None, 30)
# concrete_walking = pygame.mixer.Sound('assets/concrete.mp3')

# ==========================
# AUDIO FILES
# ==========================
sfx_start = pygame.mixer.Sound('assets/ValourAgainstAllOddsTEMP.mp3')
sfx_playing = pygame.mixer.Sound('assets/DungeonTheme2.wav')
sfx_victory = pygame.mixer.Sound('assets/Drum loop _01.wav')
sfx_step = pygame.mixer.Sound('assets/StepRock.wav')
sfx_lever = pygame.mixer.Sound('assets/InteractSound.wav')
sfx_wrong = pygame.mixer.Sound('assets/ErrorSound.wav')

# ======================
# TILE TYPE CONSTANTS
# ======================
T_WALL = 1
T_ICE = 0
T_ROCK = 2
T_SAFE = 3
T_BLACK = 4
T_LAVA = 4
# ======================
# GRIDS
# ======================
def make_floor_grid(next_direction, prev_direction, room_name):
    g = [[T_WALL] * GRID_COLS for _ in range(GRID_ROWS)]
    if room_name == teleportation:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                if col == 5 or col == 10:
                    g[row][col] = T_SAFE
                if (row == 1 or row == 2 or row == 3 or row == 8 or row == 9 or row == 10) and (
                        col != 4 and col != 6 and col != 9 and col != 11 and col != 7 and col != 8):
                    g[row][col] = T_SAFE
                if (row == 5 or row == 6) and (col == 4 or col == 11):
                    g[row][col] = T_SAFE
                if (col == 7 or col == 8) and (row != 3 and row != 8):
                    g[row][col] = T_SAFE
                if (row == 5 or row == 6) and (col == 1 or col == 2 or col == 13 or col == 14):
                    g[row][col] = T_SAFE
    elif room_name == MemoryPathRoom:
        return MemoryPathRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == HiddenPathRoom:
        return HiddenPathRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == LavaRoom:
        return LavaRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == NoBacktrackRoom:
        return NoBacktrackRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == FrictionlessFloor:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                if (col == 1 and row == 2) or (col == 3 and row == 8) or (col == 5 and row == 6) or (
                        col == 6 and row == 5) or (col == 6 and row == 7) or (col == 7 and row == 2) or (
                        col == 8 and row == 8) or (col == 10 and row == 4) or (col == 11 and row == 5) or (
                        col == 12 and row == 3) or (col == 12 and row == 9) or (col == 13 and row == 6):
                    g[row][col] = T_ROCK
                elif (col == 1 and (row == 5 or row == 6)) or (col == GRID_COLS - 2 and (row == 5 or row == 6)) or (
                        row == 1 and (col == 7 or col == 8)) or (row == GRID_ROWS - 2 and (col == 7 or col == 8)) or (
                        col == 6 and row == 6):
                    g[row][col] = T_SAFE
                else:
                    g[row][col] = T_ICE
    else:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                g[row][col] = T_SAFE
    if next_direction == "east":
        g[5][GRID_COLS - 1] = T_SAFE
        g[6][GRID_COLS - 1] = T_SAFE
    if next_direction == "west":
        g[5][0] = T_SAFE
        g[6][0] = T_SAFE
    if next_direction == "north":
        g[0][7] = T_SAFE
        g[0][8] = T_SAFE
    if next_direction == "south":
        g[GRID_ROWS - 1][7] = T_SAFE
        g[GRID_ROWS - 1][8] = T_SAFE
    if prev_direction == "east":
        g[5][GRID_COLS - 1] = T_SAFE
        g[6][GRID_COLS - 1] = T_SAFE
    if prev_direction == "west":
        g[5][0] = T_SAFE
        g[6][0] = T_SAFE
    if prev_direction == "north":
        g[0][7] = T_SAFE
        g[0][8] = T_SAFE
    if prev_direction == "south":
        g[GRID_ROWS - 1][7] = T_SAFE
        g[GRID_ROWS - 1][8] = T_SAFE
    return g


# ======================
# DOOR PIXEL RECTS
# Each door is 2 tiles.  We store (left_rect, right_rect).
# For west/east doors "left" = lower row number (top tile).
# For north/south doors "left" = lower col number.
# ======================
WEST_DOOR_RECTS = (pygame.Rect(0, 6 * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                   pygame.Rect(0, 5 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
EAST_DOOR_RECTS = (pygame.Rect((GRID_COLS - 1) * TILE_SIZE, 5 * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                   pygame.Rect((GRID_COLS - 1) * TILE_SIZE, 6 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
NORTH_DOOR_RECTS = (pygame.Rect(7 * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE),
                    pygame.Rect(8 * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
SOUTH_DOOR_RECTS = (pygame.Rect(8 * TILE_SIZE, (GRID_ROWS - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    pygame.Rect(7 * TILE_SIZE, (GRID_ROWS - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
door_rects = {"north": NORTH_DOOR_RECTS,
              "south": SOUTH_DOOR_RECTS,
              "east": EAST_DOOR_RECTS,
              "west": WEST_DOOR_RECTS,
              }
# ======================
# GAME STATE
# ======================
gus_x = 1 * TILE_SIZE
gus_y = 5 * TILE_SIZE# comments in python start with a hash instead of //
# pylint: disable=no-member
import pygame
import sys
from datetime import datetime
import random
pygame.init()
# ======================
# CONSTANTS
# ======================
TILE_SIZE = 64
SCREEN_WIDTH = 16 * TILE_SIZE
SCREEN_HEIGHT = 12 * TILE_SIZE
SPEED = 8
GRID_COLS = SCREEN_WIDTH // TILE_SIZE  # 16
GRID_ROWS = SCREEN_HEIGHT // TILE_SIZE  # 12
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.init()
clock = pygame.time.Clock()
# ======================
# game files
# ======================
import start_room
import win_room
import simon_says
import FrictionlessFloor
import teleportation
import switch_grid
import LavaRoom
import MemoryPathRoom
import NoBacktrackRoom
import HiddenPathRoom
import swapbuckets
games = [simon_says, FrictionlessFloor, teleportation, switch_grid, LavaRoom, MemoryPathRoom, NoBacktrackRoom, HiddenPathRoom, swapbuckets]

from menus import MenuManager
from leaderboard import LeaderboardManager

# ===========================
# game information
# ===========================
pygame.display.set_caption("start room")
menu = MenuManager(screen)
lb = LeaderboardManager(screen)
d0 = datetime(2008, 8, 18)
d1 = datetime.now()
delta = d1 - d0
random.seed(delta.days)
# ======================
# ASSETS
# ======================
def load_img(path, alpha=False):
    img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

# Door assets  — Left tile = the tile closer to col 0 / row 0 of the pair
door_imgs = {
    "west_left_open": load_img('assets/WestLeftDoorOpen.png', alpha=True),
    "west_right_open": load_img('assets/WestRightDoorOpen.png', alpha=True),
    "west_left_closed": load_img('assets/WestLeftDoorClosed.png', alpha=True),
    "west_right_closed": load_img('assets/WestRightDoorClosed.png', alpha=True),
    "east_left_open": load_img('assets/EastLeftDoorOpen.png', alpha=True),
    "east_right_open": load_img('assets/EastRightDoorOpen.png', alpha=True),
    "east_left_closed": load_img('assets/EastLeftDoorClosed.png', alpha=True),
    "east_right_closed": load_img('assets/EastRightDoorClosed.png', alpha=True),
    "north_left_open": load_img('assets/NorthLeftDoorOpen.png', alpha=True),
    "north_right_open": load_img('assets/NorthRightDoorOpen.png', alpha=True),
    "north_left_closed": load_img('assets/NorthLeftDoorClosed.png', alpha=True),
    "north_right_closed": load_img('assets/NorthRightDoorClosed.png', alpha=True),
    "south_left_open": load_img('assets/SouthLeftDoorOpen.png', alpha=True),
    "south_right_open": load_img('assets/SouthRightDoorOpen.png', alpha=True),
    "south_left_closed": load_img('assets/SouthLeftDoorClosed.png', alpha=True),
    "south_right_closed": load_img('assets/SouthRightDoorClosed.png', alpha=True),
}
wall_img = load_img('assets/Wall1.png')  # wall border
floor_img = load_img('assets/Path2.png')  # safe / normal floor
ice_img = load_img('assets/IceFloor.png', alpha=True)  # slippery ice
rock_img = load_img('assets/Rock.png', alpha=True)

#pause_btn_img = pygame.image.load('assets/PauseButton.png').convert_alpha()  # Pause button
#pause_btn_img = pygame.transform.scale(pause_btn_img, (48, 48))

# Player sprites
player_imgs = {
    "down": load_img('assets/Char1-1.png'),
    "right": load_img('assets/Char1-2.png'),
    "up": load_img('assets/Char1-3.png'),
    "left": load_img('assets/Char1-4.png'),
}
for img in player_imgs.values():
    img.set_colorkey((0, 0, 0))
movinggus = player_imgs["down"]
# Tile images
font = pygame.font.Font(None, 30)


# ======================
# TILE TYPE CONSTANTS
# ======================
T_WALL = 1
T_ICE = 0
T_ROCK = 2
T_SAFE = 3
T_BLACK = 4
T_LAVA = 4
# ======================
# GRIDS
# ======================
def make_floor_grid(next_direction, prev_direction, room_name):
    g = [[T_WALL] * GRID_COLS for _ in range(GRID_ROWS)]
    if room_name == teleportation:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                if col == 5 or col == 10:
                    g[row][col] = T_SAFE
                if (row == 1 or row == 2 or row == 3 or row == 8 or row == 9 or row == 10) and (
                        col != 4 and col != 6 and col != 9 and col != 11 and col != 7 and col != 8):
                    g[row][col] = T_SAFE
                if (row == 5 or row == 6) and (col == 4 or col == 11):
                    g[row][col] = T_SAFE
                if (col == 7 or col == 8) and (row != 3 and row != 8):
                    g[row][col] = T_SAFE
                if (row == 5 or row == 6) and (col == 1 or col == 2 or col == 13 or col == 14):
                    g[row][col] = T_SAFE
    elif room_name == MemoryPathRoom:
        return MemoryPathRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == HiddenPathRoom:
        return HiddenPathRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == LavaRoom:
        return LavaRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == NoBacktrackRoom:
        return NoBacktrackRoom.make_grid(next_direction, prev_direction, GRID_COLS, GRID_ROWS)
    elif room_name == FrictionlessFloor:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                if (col == 1 and row == 2) or (col == 3 and row == 8) or (col == 5 and row == 6) or (
                        col == 6 and row == 5) or (col == 6 and row == 7) or (col == 7 and row == 2) or (
                        col == 8 and row == 8) or (col == 10 and row == 4) or (col == 11 and row == 5) or (
                        col == 12 and row == 3) or (col == 12 and row == 9) or (col == 13 and row == 6):
                    g[row][col] = T_ROCK
                elif (col == 1 and (row == 5 or row == 6)) or (col == GRID_COLS - 2 and (row == 5 or row == 6)) or (
                        row == 1 and (col == 7 or col == 8)) or (row == GRID_ROWS - 2 and (col == 7 or col == 8)) or (
                        col == 6 and row == 6):
                    g[row][col] = T_SAFE
                else:
                    g[row][col] = T_ICE
    else:
        for row in range(1, GRID_ROWS - 1):
            for col in range(1, GRID_COLS - 1):
                g[row][col] = T_SAFE
    if next_direction == "east":
        g[5][GRID_COLS - 1] = T_SAFE
        g[6][GRID_COLS - 1] = T_SAFE
    if next_direction == "west":
        g[5][0] = T_SAFE
        g[6][0] = T_SAFE
    if next_direction == "north":
        g[0][7] = T_SAFE
        g[0][8] = T_SAFE
    if next_direction == "south":
        g[GRID_ROWS - 1][7] = T_SAFE
        g[GRID_ROWS - 1][8] = T_SAFE
    if prev_direction == "east":
        g[5][GRID_COLS - 1] = T_SAFE
        g[6][GRID_COLS - 1] = T_SAFE
    if prev_direction == "west":
        g[5][0] = T_SAFE
        g[6][0] = T_SAFE
    if prev_direction == "north":
        g[0][7] = T_SAFE
        g[0][8] = T_SAFE
    if prev_direction == "south":
        g[GRID_ROWS - 1][7] = T_SAFE
        g[GRID_ROWS - 1][8] = T_SAFE
    return g


# ======================
# DOOR PIXEL RECTS
# Each door is 2 tiles.  We store (left_rect, right_rect).
# For west/east doors "left" = lower row number (top tile).
# For north/south doors "left" = lower col number.
# ======================
WEST_DOOR_RECTS = (pygame.Rect(0, 6 * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                   pygame.Rect(0, 5 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
EAST_DOOR_RECTS = (pygame.Rect((GRID_COLS - 1) * TILE_SIZE, 5 * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                   pygame.Rect((GRID_COLS - 1) * TILE_SIZE, 6 * TILE_SIZE, TILE_SIZE, TILE_SIZE))
NORTH_DOOR_RECTS = (pygame.Rect(7 * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE),
                    pygame.Rect(8 * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
SOUTH_DOOR_RECTS = (pygame.Rect(8 * TILE_SIZE, (GRID_ROWS - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    pygame.Rect(7 * TILE_SIZE, (GRID_ROWS - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
door_rects = {"north": NORTH_DOOR_RECTS,
              "south": SOUTH_DOOR_RECTS,
              "east": EAST_DOOR_RECTS,
              "west": WEST_DOOR_RECTS,
              }
# ======================
# GAME STATE
# ======================
gus_x = 1 * TILE_SIZE
gus_y = 5 * TILE_SIZE
target_x = gus_x
target_y = gus_y
notify_text = ""
stepCount = 0
notify_timer = 0
NOTIFY_DURATION = 2000

game_state = "START"
previous_state = "START"
spawn_invisible = False


_current_music = "NONE"


# ======================
# HELPERS
# ======================
def grid_col(px): return px // TILE_SIZE


def grid_row(py): return py // TILE_SIZE


def is_blocked(grid, col, row):
    if col < 0 or col >= GRID_COLS or row < 0 or row >= GRID_ROWS:
        return True
    return grid[row][col] in (T_WALL, T_ROCK)


def is_safe(grid, col, row):
    if col < 0 or col >= GRID_COLS or row < 0 or row >= GRID_ROWS:
        return False
    return grid[row][col] == T_SAFE


def show_notify(text):
    global notify_text, notify_timer
    notify_text = text
    notify_timer = pygame.time.get_ticks()


def set_previous_direction(direction):
    if direction == "north":
        return "south"
    elif direction == "east":
        return "west"
    elif direction == "south":
        return "north"
    elif direction == "west":
        return "east"
    else:
        return ""


# ======================
# DRAW HELPERS
# ======================
def draw_grid_lines(surface):
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(surface, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, (100, 100, 100), (0, y), (SCREEN_WIDTH, y))


def draw_room_tiles(surface, grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            tile = grid[row][col]
            if tile == T_WALL:
                surface.blit(wall_img, rect)
            elif tile == T_ROCK:
                surface.blit(floor_img, rect)
                surface.blit(rock_img, rect)
            elif tile == T_SAFE:
                surface.blit(floor_img, rect)
            elif tile == T_BLACK:
                surface.blit(floor_img, rect)
                pygame.draw.rect(surface, (20, 20, 20), rect)
            elif tile == T_LAVA:
                surface.blit(floor_img, rect)
            else:  # T_ICE
                surface.blit(ice_img, rect)


def draw_door_pair(surface, rects, dir_key, is_open):
    """Blit the left and right sprites for one door."""
    state = "open" if is_open else "closed"
    surface.blit(door_imgs[f"{dir_key}_left_{state}"], rects[0])
    surface.blit(door_imgs[f"{dir_key}_right_{state}"], rects[1])


def draw_notify(surface):
    if notify_text and pygame.time.get_ticks() - notify_timer < NOTIFY_DURATION:
        txt = font.render(notify_text, True, (0, 0, 0))
        surface.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 20))


# =========================
# GAME GENERATION
# =========================
dungeon = [[0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0]]
startx = random.randint(0, len(dungeon) - 1)
starty = random.randint(0, len(dungeon) - 1)
total_length = 5


def generate_dungeon(x, y, path_length):
    # starting point marked
    dungeon[x][y] = path_length
    directions = []
    # filling out the path
    i = path_length - 1
    while i > 0:
        direction = random.randint(1, 4)
        match direction:
            case 1:  # UP
                x -= 1
                if (x < 0 or x >= len(dungeon) - 1 or dungeon[x][y] != 0):
                    x += 1
                else:
                    dungeon[x][y] = i
                    directions.append("north")
                    i -= 1
            case 2:  # DOWN
                x += 1
                if x < 0 or x >= len(dungeon) - 1 or dungeon[x][y] != 0:
                    x -= 1
                else:
                    dungeon[x][y] = i
                    directions.append("south")
                    i -= 1
            case 3:  # LEFT
                y -= 1
                if (y < 0 or y >= len(dungeon) - 1 or dungeon[x][y] != 0):
                    y += 1
                else:
                    dungeon[x][y] = i
                    directions.append("west")
                    i -= 1
            case 4:  # RIGHT
                y += 1
                if (y < 0 or y >= len(dungeon) - 1) or dungeon[x][y] != 0:
                    y -= 1
                else:
                    dungeon[x][y] = i
                    directions.append("east")
                    i -= 1
    z = 0
    while z < len(dungeon):
        print(dungeon[z])
        z += 1

    x = 0
    while x < len(directions):
        print(directions[x])
        x += 1
    return directions


navigation = generate_dungeon(startx, starty, total_length)
rooms = [{"roomID": "start", "next direction": navigation[0], "previous direction": "none", "Room": start_room,
          "have entered": False},
          {"roomID": "puzzle1", "next direction": navigation[1],
           "previous direction": set_previous_direction(navigation[0]), "Room": games[random.randint(0,len(games)-1)], "have entered": False},
          {"roomID": "puzzle2", "next direction":navigation[2], "previous direction":set_previous_direction(navigation[1]), "Room": games[random.randint(0,len(games)-1)], "have entered": False},
          {"roomID": "puzzle3", "next direction":navigation[3],"previous direction":set_previous_direction(navigation[2]), "Room": games[random.randint(0,len(games)-1)], "have entered": False},
          {"roomID": "end", "next direction": "none", "previous direction": set_previous_direction(navigation[3]),
          "Room": win_room, "have entered": True}]
index = 0
#pause_btn_rect = pygame.Rect(SCREEN_WIDTH - 58, 10, 48, 48)


def slide_destination(grid, col, row, xcol, xrow):
    nuc, nur = col + xcol, row + xrow
    if is_blocked(grid, nuc, nur):
        return col, row

    if is_safe(grid, col, row):
        if is_safe(grid, nuc, nur):
            return nuc, nur
        col, row = nuc, nur
        nuc, nur = col + xcol, row + xrow
        if is_blocked(grid, nuc, nur):
            return col, row

    while True:
        lookahead_c = nuc + xcol
        lookahead_r = nur + xrow
        if is_blocked(grid, lookahead_c, lookahead_r):
            break
        if is_safe(grid, nuc, nur):
            break
        nuc += xcol
        nur += xrow

    return nuc, nur


# ======================
# MAIN LOOP
# ======================
running = True
while running:
    clock.tick(60)

    if game_state in ("START", "LEADERBOARD") and _current_music != "START":
        sfx_victory.stop()
        sfx_playing.stop()
        sfx_start.play(-1)
        sfx_start.set_volume(0.3)
        _current_music = "START"
    elif game_state in ("PLAYING", "PAUSED") and _current_music != "PLAYING":
        sfx_start.stop()
        sfx_victory.stop()
        sfx_playing.play(-1)
        sfx_playing.set_volume(0.3)
        _current_music = "PLAYING"
    elif game_state == "VICTORY" and _current_music != "VICTORY":
        sfx_start.stop()
        sfx_playing.stop()
        sfx_victory.play(-1)
        sfx_victory.set_volume(1)
        _current_music = "VICTORY"

    if game_state == "START":
        action = menu.draw_start_menu()
        if action == "START":
            index = 0
            stepCount = 0
            gus_x = 1 * TILE_SIZE
            gus_y = 5 * TILE_SIZE
            target_x = gus_x
            target_y = gus_y
            for r in rooms:
                r["have entered"] = False
            rooms[-1]["have entered"] = True
            game_state = "PLAYING"
        elif action == "LEADERBOARD":
            previous_state = "START"
            game_state = "LEADERBOARD"
        elif action == "QUIT":
            running = False
    elif game_state == "PLAYING":
        current = rooms[index]
        start_grid = make_floor_grid(current["next direction"], current["previous direction"], current["Room"])
        is_moving = False
        interact = False
        go_next = False
        go_back = False
        if not current["have entered"]:
            current["Room"].set_solved(False)
            if current["Room"] == MemoryPathRoom:
                MemoryPathRoom.init(current["next direction"])
            if current["Room"] == LavaRoom:
                LavaRoom.init(current["previous direction"])
            if current["Room"] == HiddenPathRoom:
                HiddenPathRoom.init(current["previous direction"])
            current["have entered"] = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    interact = True
                elif event.key == pygame.K_ESCAPE:
                    game_state = "PAUSED"
                    break
                # Movement — only when fully stopped on a tile
                if gus_x == target_x and gus_y == target_y:
                    dcol = drow = 0
                    if event.key in (pygame.K_d, pygame.K_RIGHT):
                        movinggus = player_imgs["right"]
                        dcol = 1
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        movinggus = player_imgs["left"]
                        dcol = -1
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        movinggus = player_imgs["down"]
                        drow = 1
                    elif event.key in (pygame.K_w, pygame.K_UP):
                        movinggus = player_imgs["up"]
                        drow = -1
                    if dcol != 0 or drow != 0:
                        cur_col = grid_col(gus_x)
                        cur_row = grid_row(gus_y)
                        if current["Room"] == FrictionlessFloor:
                            nc, nr = slide_destination(start_grid, cur_col, cur_row, dcol, drow)
                            if nc != cur_col or nr != cur_row:
                                target_x = nc * TILE_SIZE
                                target_y = nr * TILE_SIZE
                                stepCount += 1
                               
                                sfx_step.play()
                        else:
                            # Invert controls for LavaRoom
                            if current["Room"] == LavaRoom and LavaRoom.get_controls_inverted():
                                dcol, drow = -dcol, -drow
                            nc, nr = cur_col + dcol, cur_row + drow
                            if not is_blocked(start_grid, nc, nr):
                                target_x = nc * TILE_SIZE
                                target_y = nr * TILE_SIZE
                                stepCount += 1
                                
                                sfx_step.play()
                                if current["Room"] == NoBacktrackRoom:
                                    stepCount += NoBacktrackRoom.on_move(nc, nr)
                                if current["Room"] == LavaRoom:
                                    LavaRoom.on_move()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    interact = False
        if game_state == "PAUSED":
            continue
        # ---- smooth pixel movement ----
        if gus_x < target_x and not is_moving:
            gus_x += SPEED
            is_moving = True
        elif gus_x > target_x:
            gus_x -= SPEED
            is_moving = True
        if gus_y < target_y:
            gus_y += SPEED
            is_moving = True
        elif gus_y > target_y:
            gus_y -= SPEED
            is_moving = True
        # ---- hitbox ----
        hitbox = movinggus.get_bounding_rect()
        hitbox.x += gus_x
        hitbox.y += gus_y
        # =======================
        # Logic for the victory room
        # =======================
        if current["Room"] == win_room and current["Room"].get_solved():
            lb.submit("Player", stepCount)
            game_state = "VICTORY"
        # ======================
        # RENDERING
        # ======================
        screen.fill((150, 150, 150))
        draw_room_tiles(screen, start_grid)
        draw_grid_lines(screen)
        current["Room"].render(screen, hitbox, interact, TILE_SIZE)

        # logic for memory path room
        if current["Room"] == MemoryPathRoom:
            def set_teleport(col, row):
                global gus_x, gus_y, target_x, target_y
                gus_x = col * TILE_SIZE
                gus_y = row * TILE_SIZE
                target_x = gus_x
                target_y = gus_y
                hitbox.x = gus_x
                hitbox.y = gus_y

            if gus_x == target_x and gus_y == target_y:
                cur_col = gus_x // TILE_SIZE
                cur_row = gus_y // TILE_SIZE
                dest = MemoryPathRoom.step_on(cur_col, cur_row)
                if dest:
                    set_teleport(*dest)

            if interact:
                MemoryPathRoom.try_lever(gus_x // TILE_SIZE, gus_y // TILE_SIZE, sfx_lever)

        # logic for the hidden path room
        if current["Room"] == HiddenPathRoom:
            def set_teleport(col, row):
                global gus_x, gus_y, target_x, target_y
                gus_x = col * TILE_SIZE
                gus_y = row * TILE_SIZE
                target_x = gus_x
                target_y = gus_y
                hitbox.x = gus_x
                hitbox.y = gus_y

            if gus_x == target_x and gus_y == target_y:
                dest = HiddenPathRoom.step_on(gus_x // TILE_SIZE, gus_y // TILE_SIZE)
                if dest:
                    set_teleport(*dest)


            if interact:
                HiddenPathRoom.try_lever(gus_x // TILE_SIZE, gus_y // TILE_SIZE, sfx_lever)

        # Logic for Lava room
        if current["Room"] == LavaRoom:
            def set_teleport(col, row):
                global gus_x, gus_y, target_x, target_y
                gus_x = col * TILE_SIZE
                gus_y = row * TILE_SIZE
                target_x = gus_x
                target_y = gus_y
                hitbox.x = gus_x
                hitbox.y = gus_y

            if gus_x == target_x and gus_y == target_y:
                dest = LavaRoom.step_on(gus_x // TILE_SIZE, gus_y // TILE_SIZE)
                if dest:
                    set_teleport(*dest)

            if interact:
                LavaRoom.try_lever(gus_x // TILE_SIZE, gus_y // TILE_SIZE, sfx_lever)

        # logic for the teleportation for the teleportation room
        if current["Room"] == teleportation:
            current["Room"].set_solved(True)

            def set_teleport(x, y):
                global target_x
                global target_y
                global gus_y
                global gus_x
                n_x = x
                n_y = y
                gus_x = n_x
                gus_y = n_y
                target_x = n_x
                target_y = n_y
                hitbox.x = gus_x
                hitbox.y = gus_y

            if gus_x == TILE_SIZE * 2 and gus_y == TILE_SIZE * 5:
                set_teleport(TILE_SIZE * 14, TILE_SIZE * 2)
            if gus_x == TILE_SIZE * 14 and gus_y == TILE_SIZE:
                set_teleport(TILE_SIZE * 2, TILE_SIZE * 6)
            if gus_x == TILE_SIZE * 12 and gus_y == TILE_SIZE * 3:
                set_teleport(TILE_SIZE * 5, TILE_SIZE * 4)
            if gus_x == TILE_SIZE * 5 and gus_y == TILE_SIZE * 3:
                set_teleport(TILE_SIZE * 12, TILE_SIZE * 2)
            if gus_x == TILE_SIZE * 4 and gus_y == TILE_SIZE * 6:
                set_teleport(TILE_SIZE * 7, TILE_SIZE * 5)
            if gus_x == TILE_SIZE * 7 and gus_y == TILE_SIZE * 4:
                set_teleport(TILE_SIZE * 4, TILE_SIZE * 5)
            if gus_x == TILE_SIZE * 5 and gus_y == TILE_SIZE * 8:
                set_teleport(TILE_SIZE * 12, TILE_SIZE * 9)
            if gus_x == TILE_SIZE * 12 and gus_y == TILE_SIZE * 8:
                set_teleport(TILE_SIZE * 5, TILE_SIZE * 7)
            if gus_x == TILE_SIZE * 14 and gus_y == TILE_SIZE * 10:
                set_teleport(TILE_SIZE * 8, TILE_SIZE)
            if gus_x == TILE_SIZE * 8 and gus_y == TILE_SIZE * 2:
                set_teleport(TILE_SIZE * 14, TILE_SIZE * 9)
            if gus_x == TILE_SIZE * 8 and gus_y == TILE_SIZE * 7:
                set_teleport(TILE_SIZE * 11, TILE_SIZE * 5)
            if gus_x == TILE_SIZE * 11 and gus_y == TILE_SIZE * 6:
                set_teleport(TILE_SIZE * 8, TILE_SIZE * 6)
            if gus_x == TILE_SIZE * 10 and gus_y == TILE_SIZE * 3:
                set_teleport(TILE_SIZE * 3, TILE_SIZE * 2)
            if gus_x == TILE_SIZE * 3 and gus_y == TILE_SIZE * 3:
                set_teleport(TILE_SIZE * 10, TILE_SIZE * 4)
            if gus_x == TILE_SIZE * 10 and gus_y == TILE_SIZE * 8:
                set_teleport(TILE_SIZE * 3, TILE_SIZE * 9)
            if gus_x == TILE_SIZE * 3 and gus_y == TILE_SIZE * 8:
                set_teleport(TILE_SIZE * 10, TILE_SIZE * 7)
            if gus_x == TILE_SIZE and gus_y == TILE_SIZE * 10:
                set_teleport(TILE_SIZE * 8, TILE_SIZE * 10)
            if gus_x == TILE_SIZE * 8 and gus_y == TILE_SIZE * 9:
                set_teleport(TILE_SIZE, TILE_SIZE * 9)
            if gus_x == TILE_SIZE and gus_y == TILE_SIZE:
                set_teleport(TILE_SIZE * 13, TILE_SIZE * 6)
            if gus_x == TILE_SIZE * 13 and gus_y == TILE_SIZE * 5:
                set_teleport(TILE_SIZE, TILE_SIZE * 2)
        # this creates the doors to the next room and sets player in proper position
        if current["next direction"] != "none":
            next_doors = door_rects[current["next direction"]]
            draw_door_pair(screen, next_doors, current["next direction"], is_open=current["Room"].get_solved())
            if hitbox.colliderect(next_doors[0]) or hitbox.colliderect(next_doors[1]) and current["Room"].get_solved():
                if current["next direction"] == "north":
                    new_y = (GRID_ROWS - 2) * TILE_SIZE
                    gus_y = new_y
                    target_y = new_y
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                if current["next direction"] == "south":
                    new_y = TILE_SIZE
                    gus_y = new_y
                    target_y = new_y
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                if current["next direction"] == "east":
                    new_x = TILE_SIZE
                    gus_x = new_x
                    target_x = new_x
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                if current["next direction"] == "west":
                    new_x = (GRID_COLS - 2) * TILE_SIZE
                    gus_x = new_x
                    target_x = new_x
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                go_next = True
        if current["previous direction"] != "none":
            previous_doors = door_rects[current["previous direction"]]
            draw_door_pair(screen, previous_doors, current["previous direction"], is_open=True)
            if hitbox.colliderect(previous_doors[0]) or hitbox.colliderect(previous_doors[1]):
                if current["previous direction"] == "north":
                    new_y = (GRID_ROWS - 2) * TILE_SIZE
                    gus_y = new_y
                    target_y = new_y
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                if current["previous direction"] == "south":
                    new_y = TILE_SIZE
                    gus_y = new_y
                    target_y = new_y
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                if current["previous direction"] == "west":
                    target_x = (GRID_COLS - 2) * TILE_SIZE
                if current["previous direction"] == "east":
                    new_x = TILE_SIZE
                    gus_x = new_x
                    target_x = new_x
                    hitbox.x = gus_x
                    hitbox.y = gus_y
                go_back = True
        if go_next:
            index += 1
            if index >= len(rooms):
                lb.submit("Player", stepCount)
                game_state = "VICTORY"
                index = len(rooms) - 1
            print(index)
        if go_back:
            index -= 1
            print(index)

        # ---- step counter + player sprite (always drawn last / on top) ----
        step_surf = font.render(f"Steps: {stepCount}", True, (255, 255, 255))
        screen.blit(step_surf, (10, SCREEN_HEIGHT - 30))
        screen.blit(movinggus, (gus_x, gus_y))
        #screen.blit(pause_btn_img, pause_btn_rect)

    elif game_state == "PAUSED":
        start_grid = make_floor_grid(current["next direction"], current["previous direction"], current["Room"])
        draw_room_tiles(screen, start_grid)
        draw_grid_lines(screen)
        screen.blit(movinggus, (gus_x, gus_y))
        #screen.blit(pause_btn_img, pause_btn_rect)
        action = menu.draw_pause_menu()
        if action == "RESUME":
            game_state = "PLAYING"
        elif action == "QUIT":
            game_state = "START"

    elif game_state == "VICTORY":
        action = menu.draw_victory_menu()
        if action == "RETRY":
            index = 0
            stepCount = 0
            gus_x = 1 * TILE_SIZE
            gus_y = 5 * TILE_SIZE
            target_x = gus_x
            target_y = gus_y
            for r in rooms:
                r["have entered"] = False
            rooms[-1]["have entered"] = True
            game_state = "PLAYING"
        elif action == "LEADERBOARD":
            previous_state = "VICTORY"
            game_state = "LEADERBOARD"
        elif action == "QUIT":
            game_state = "START"

    elif game_state == "LEADERBOARD":
        action = lb.draw(screen)
        if action == "BACK":
            game_state = previous_state
    pygame.display.flip()
pygame.quit()
sys.exit()
