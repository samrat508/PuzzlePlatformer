"""
HiddenPathRoom.py — puzzle room module for main.py
Same interface as other rooms:
    render(surface, hitbox, interact, tile_size)
    get_solved() -> bool
    set_solved(bool)
    make_grid(next_dir, prev_dir, grid_cols, grid_rows) -> grid
    step_on(col, row) -> (col, row) or None   [called by main.py]
    try_lever(col, row)                        [called by main.py on SPACE]
"""
import pygame

# ======================
# PUZZLE DATA
# ======================
LEVER_POS = (9, 5)

CORRECT_PATH = {
    (1, 1), (1, 2), (1, 3), (1, 5), (1, 6), (1, 10),
    (2, 1), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
    (3, 1), (3, 3),
    (4, 1), (4, 3), (4, 4), (4, 7), (4, 8), (4, 9),
    (5, 2), (5, 4), (5, 5), (5, 6), (5, 9),
    (6, 2), (6, 6), (6, 7), (6, 8), (6, 9),
    (7, 1), (7, 2), (7, 6), (7, 9), (7, 10),
    (8, 1), (8, 2), (8, 6), (8, 9), (8, 10),
    (9, 2), (9, 5), (9, 6), (9, 9),
    (10, 2), (10, 3), (10, 4), (10, 5), (10, 6),
    (11, 2), (11, 6), (11, 7), (11, 8), (11, 9),
    (12, 2), (12, 3), (12, 9),
    (13, 3), (13, 6), (13, 7), (13, 8), (13, 9),
    (14, 1), (14, 2), (14, 3), (14, 5), (14, 6)
}

# Tiles exempt from wrong-tile penalty (doors, spawn)
_EXEMPT = {
    (1, 5), (1, 6),          # west door
    (14, 5), (14, 6),        # east door
    (7, 0), (8, 0),          # north door
    (7, 11), (8, 11),        # south door
}

# Spawn position set dynamically by init() based on entry direction
SPAWN_COL = 1
SPAWN_ROW = 5

_SPAWN_BY_DIR = {
    "east":  (14, 5),
    "west":  (1,  5),
    "north": (7,  1),
    "south": (7, 10),
}

# ======================
# MODULE STATE
# ======================
_solved          = False
_lever_activated = False
_discovered      = set()
_revealed_wrong  = set()

_notify_text  = ""
_notify_timer = 0
NOTIFY_DURATION = 2500

_assets = {}

# ======================
# PUBLIC API
# ======================
def get_solved():
    return _solved

def init(prev_dir):
    """Call when entering the room so respawn matches the entry door."""
    global SPAWN_COL, SPAWN_ROW
    pos = _SPAWN_BY_DIR.get(prev_dir, (1, 5))
    SPAWN_COL, SPAWN_ROW = pos
    # Reset discovered to new spawn point
    _discovered.clear()
    _discovered.add((SPAWN_COL, SPAWN_ROW))

def set_solved(solved):
    global _solved, _lever_activated, _discovered, _revealed_wrong
    _solved          = solved
    _lever_activated = False
    _discovered      = {(SPAWN_COL, SPAWN_ROW)}
    _revealed_wrong  = set()

def try_lever(col, row, sfx = None):
    """Called by main.py on SPACE press with exact gus position."""
    global _lever_activated, _solved
    if (col, row) == LEVER_POS and not _lever_activated:
        _lever_activated = True
        _solved          = True
        #_show_notify("Lever activated! Doors unlocked.")
        if "lever" in _assets:
            _assets["lever"].play()

def step_on(col, row):
    """
    Called by main.py when gus lands on a tile.
    Returns (spawn_col, spawn_row) to teleport on wrong tile, else None.
    """
    global _discovered, _revealed_wrong
    pos = (col, row)

    # Glow discovered correct path tiles
    if pos in CORRECT_PATH:
        _discovered.add(pos)
        return None

    # Wrong tile — reveal as lava and respawn
    if pos not in _EXEMPT and pos != LEVER_POS:
        if pos not in _revealed_wrong:
            _revealed_wrong.add(pos)
            #_show_notify("Wrong path! Revealed as lava.")
            if "error" in _assets:
                _assets["error"].play()
        else:
            # Already revealed — still respawn
            #_show_notify("Wrong tile! Back to the start.")
            if "error" in _assets:
                _assets["error"].play()
        return (SPAWN_COL, SPAWN_ROW)

    return None

def render(surface, hitbox, interact, tile_size):
    """Called once per frame by main.py."""
    _load_assets(tile_size)
    font = _assets["font"]
    sw, sh = surface.get_width(), surface.get_height()

    # Draw discovered correct tiles
    for col, row in _discovered:
        rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
        surface.blit(_assets["correct"], rect)

    # Draw revealed wrong tiles as lava
    for col, row in _revealed_wrong:
        rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
        surface.blit(_assets["incorrect"], rect)

    # Draw lever
    rect = pygame.Rect(LEVER_POS[0] * tile_size, LEVER_POS[1] * tile_size, tile_size, tile_size)
    surface.blit(_assets["correct"], rect)
    state = "lever_on" if _lever_activated else "lever_off"
    surface.blit(_assets[state], rect)

    # HUD prompt when standing on lever
    pc = hitbox.centerx // tile_size
    pr = hitbox.centery // tile_size
    if (pc, pr) == LEVER_POS and not _lever_activated:
        p = font.render("Press SPACE to pull the lever", True, (255, 255, 200))
        surface.blit(p, (sw // 2 - p.get_width() // 2, sh - 55))

    _draw_notify(surface, font, sw)

# ======================
# GRID EXPORT
# ======================
T_WALL = 1
T_SAFE = 3

def make_grid(next_dir, prev_dir, grid_cols=16, grid_rows=12):
    g = [[T_WALL] * grid_cols for _ in range(grid_rows)]
    for row in range(1, grid_rows - 1):
        for col in range(1, grid_cols - 1):
            g[row][col] = T_SAFE
    # Door gaps
    g[5][0] = T_SAFE;             g[6][0] = T_SAFE
    g[5][grid_cols-1] = T_SAFE;   g[6][grid_cols-1] = T_SAFE
    if next_dir == "north" or prev_dir == "north": g[0][7] = T_SAFE; g[0][8] = T_SAFE
    if next_dir == "south" or prev_dir == "south": g[grid_rows-1][7] = T_SAFE; g[grid_rows-1][8] = T_SAFE
    return g

# ======================
# INTERNAL HELPERS
# ======================
def _load_assets(tile_size):
    if _assets:
        return
    def img(path, alpha=False):
        i = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
        return pygame.transform.scale(i, (tile_size, tile_size))
    _assets["correct"]   = img("assets/MarblePath.png")
    _assets["incorrect"] = img("assets/Lava.png")
    _assets["lever_off"] = img("assets/MountedLeverRightOff.png", alpha=True)
    _assets["lever_on"]  = img("assets/MountedLeverRightOn.png",  alpha=True)
    _assets["font"]      = pygame.font.Font(None, 20)
    try:
        _assets["error"] = pygame.mixer.Sound("assets/ErrorSound.wav")
        _assets["lever"] = pygame.mixer.Sound("assets/InteractSound.wav")
    except Exception:
        pass  # audio optional

def _show_notify(text):
    global _notify_text, _notify_timer
    _notify_text  = text
    _notify_timer = pygame.time.get_ticks()

def _draw_notify(surface, font, screen_width):
    if _notify_text and pygame.time.get_ticks() - _notify_timer < NOTIFY_DURATION:
        txt = font.render(_notify_text, True, (255, 240, 80))
        bg  = pygame.Surface((txt.get_width()+12, txt.get_height()+8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg,  (screen_width//2 - bg.get_width()//2,  16))
        surface.blit(txt, (screen_width//2 - txt.get_width()//2, 20))
