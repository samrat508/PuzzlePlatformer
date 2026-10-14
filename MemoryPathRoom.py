"""
MemoryPathRoom.py — puzzle room module for main.py
"""
import pygame

sfx_lever = pygame.mixer.Sound('assets/InteractSound.wav')

# ====================== PUZZLE DATA ======================
CHOICE_PAIRS = [
    {"correct": (5, 4),  "wrong": (5, 6)},
    {"correct": (7, 7),  "wrong": (7, 5)},
    {"correct": (9, 6),  "wrong": (9, 4)},
    {"correct": (11, 5), "wrong": (11, 7)},
]
CORRECT_TILES   = {pair["correct"] for pair in CHOICE_PAIRS}
WRONG_TILES     = {pair["wrong"]   for pair in CHOICE_PAIRS}
ALL_BLACK_TILES = CORRECT_TILES | WRONG_TILES

INNER_WALL_TILES = {
    (1,3),(1,8),(2,4),(2,5),(2,6),(2,7),(3,3),(3,4),(3,7),(3,8),
    (4,3),(4,8),(5,3),(5,8),(6,1),(6,2),(6,3),(6,8),(6,9),(6,10),
    (7,3),(7,8),(8,3),(8,8),(9,1),(9,2),(9,3),(9,8),(9,9),(9,10),
    (10,3),(10,8),(11,2),(11,3),(11,8),(11,9),(12,2),(12,9),
    (13,2),(13,3),(13,4),(13,5),(13,6),(13,7),(13,8),(13,9),(13,10),
    (14,3),(14,8)
}
ROCK_TILES = {(5,5),(5,7),(7,4),(7,6),(9,5),(9,7),(11,4),(11,6)}

LEVER_POS        = (12, 8)
RESPAWN_POS      = (3, 5)
EXIT_PORTAL_POS  = (12, 3)   # interior portal — always visible, active after lever pulled

# One portal in front of each door — all send to RESPAWN before lever pulled
_DOOR_PORTALS = {
    "west":  (1, 4),
    "east":  (14, 5),
    "north": (8, 1),
    "south": (8, 10),
}

# ====================== MODULE STATE ======================
_solved             = False
_lever_pulled       = False
_exit_portal_active = False
_correct_stepped    = set()
_exit_dir           = "east"

_notify_text  = ""
_notify_timer = 0
NOTIFY_DURATION = 2000
_assets = {}

# ====================== PUBLIC API ======================
def get_solved():
    return _solved

def init(next_dir):
    """Call when entering the room so the exit portal matches the exit door."""
    global _exit_dir
    _exit_dir = next_dir

def set_solved(solved):
    global _solved, _lever_pulled, _exit_portal_active, _correct_stepped
    _solved             = solved
    _lever_pulled       = False
    _exit_portal_active = False
    _correct_stepped    = set()

def try_lever(col, row, sfx=None):
    """Called by main.py on SPACE press using exact gus position."""
    global _lever_pulled, _exit_portal_active, _solved
    if (col, row) == LEVER_POS and not _lever_pulled:
        if len(_correct_stepped) == len(CORRECT_TILES):
            _lever_pulled       = True
            _exit_portal_active = True
            _solved             = True
            sfx_lever.play()
            #_show_notify("Lever pulled! A portal has appeared.")
        else:
            left = len(CORRECT_TILES) - len(_correct_stepped)
            #_show_notify(f"Find the correct path first! ({left} tiles left)")

def step_on(col, row):
    """
    Called by main.py when gus lands on tile (col, row).
    Returns (dest_col, dest_row) if a teleport should happen, else None.
    """
    global _correct_stepped
    pos = (col, row)
    all_door_portals = set(_DOOR_PORTALS.values())

    # Before lever: all door portals send to respawn
    if pos in all_door_portals and not _solved:
        _correct_stepped = set()
        #_show_notify("Sent back to start!")
        return RESPAWN_POS

    if pos in WRONG_TILES and not _solved:
        _correct_stepped = set()
        #_show_notify("Wrong tile! Start again from the portal.")
        return RESPAWN_POS

    if pos in CORRECT_TILES:
        if pos not in _correct_stepped:
            _correct_stepped.add(pos)
            left = len(CORRECT_TILES) - len(_correct_stepped)
            #_show_notify(f"Correct! {left} more to find." if left else "All found! Pull the lever.")
        return None

    # Interior exit portal — only active after lever pulled
    if pos == EXIT_PORTAL_POS and _exit_portal_active:
        return _DOOR_PORTALS.get(_exit_dir)

    return None

def render(surface, hitbox, interact, tile_size):
    """Called once per frame by main.py."""
    _load_assets(tile_size)
    font = _assets["font"]
    sw, sh = surface.get_width(), surface.get_height()
    all_door_portals = set(_DOOR_PORTALS.values())

    # --- Draw portals ---
    _draw_portal(surface, *RESPAWN_POS, tile_size, (60, 180, 220))       # cyan — respawn
    _draw_portal(surface, *EXIT_PORTAL_POS, tile_size, (160, 60, 200))   # always visible purple
    for c, r in all_door_portals:
        _draw_portal(surface, c, r, tile_size, (160, 60, 200))           # door portals purple

    # Green tint on already-found correct tiles
    for c, r in _correct_stepped:
        hl = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        hl.fill((80, 255, 80, 60))
        surface.blit(hl, (c * tile_size, r * tile_size))

    # --- Lever sprite ---
    lever = _assets["lever_on"] if _lever_pulled else _assets["lever_off"]
    surface.blit(lever, (LEVER_POS[0] * tile_size, LEVER_POS[1] * tile_size))

    # --- HUD ---
    prog = font.render(f"Tiles found: {len(_correct_stepped)} / {len(CORRECT_TILES)}", True, (220, 220, 80))
    surface.blit(prog, (sw // 2 - prog.get_width() // 2, sh - 30))

    _draw_notify(surface, font, sw)

# ====================== GRID EXPORT ======================
T_WALL  = 1
T_ROCK  = 2
T_SAFE  = 3
T_BLACK = 4

def make_grid(next_dir, prev_dir, grid_cols=16, grid_rows=12):
    g = [[T_WALL] * grid_cols for _ in range(grid_rows)]
    for row in range(1, grid_rows - 1):
        for col in range(1, grid_cols - 1):
            g[row][col] = T_SAFE
    for c, r in ROCK_TILES:
        g[r][c] = T_ROCK
    for c, r in ALL_BLACK_TILES:
        g[r][c] = T_BLACK
    for c, r in INNER_WALL_TILES:
        g[r][c] = T_WALL
    g[5][0] = T_SAFE; g[6][0] = T_SAFE
    g[5][1] = T_SAFE; g[6][1] = T_SAFE
    g[5][grid_cols-1] = T_SAFE; g[6][grid_cols-1] = T_SAFE
    if next_dir == "north" or prev_dir == "north": g[0][7] = T_SAFE; g[0][8] = T_SAFE
    if next_dir == "south" or prev_dir == "south": g[grid_rows-1][7] = T_SAFE; g[grid_rows-1][8] = T_SAFE
    return g

# ====================== INTERNAL HELPERS ======================
def _load_assets(tile_size):
    if _assets:
        return
    def img(path, alpha=False):
        i = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
        return pygame.transform.scale(i, (tile_size, tile_size))
    _assets["lever_off"] = img("assets/MountedLeverBottomOff.png", alpha=True)
    _assets["lever_on"]  = img("assets/MountedLeverBottomOn.png",  alpha=True)
    _assets["font"]      = pygame.font.Font(None, 20)

def _show_notify(text):
    global _notify_text, _notify_timer
    _notify_text  = text
    _notify_timer = pygame.time.get_ticks()

def _draw_portal(surface, col, row, tile_size, color):
    cx = col * tile_size + tile_size // 2
    cy = row * tile_size + tile_size // 2
    pygame.draw.ellipse(surface, (color[0]//2, color[1]//2, color[2]//2), (cx-22, cy-16, 44, 32))
    pygame.draw.ellipse(surface, color,                                    (cx-16, cy-11, 32, 22))
    pygame.draw.ellipse(surface, (200, 180, 255),                          (cx-8,  cy-5,  16, 10))

def _draw_notify(surface, font, screen_width):
    if _notify_text and pygame.time.get_ticks() - _notify_timer < NOTIFY_DURATION:
        txt = font.render(_notify_text, True, (255, 255, 255))
        bg  = pygame.Surface((txt.get_width()+10, txt.get_height()+6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg,  (screen_width//2 - bg.get_width()//2,  17))
        surface.blit(txt, (screen_width//2 - txt.get_width()//2, 20))