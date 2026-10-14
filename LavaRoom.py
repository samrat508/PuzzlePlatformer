"""
LavaRoom.py — puzzle room module for main.py
Interface:
    render(surface, hitbox, interact, tile_size)
    get_solved() -> bool
    set_solved(bool)
    init(prev_dir)                  — call on room entry
    make_grid(next_dir, prev_dir, grid_cols, grid_rows) -> grid
    step_on(col, row) -> (col, row) or None   — called by main.py when stopped
    try_lever(col, row)             — called by main.py on SPACE
    on_move()                       — called by main.py on every successful step
"""
import pygame

# ======================
# PUZZLE DATA
# ======================
SWITCH_POS = (6, 5)

LAVA_TILES = {
    (1,4),
    (2,2),(2,4),(2,5),(2,6),(2,7),(2,9),
    (3,2),(3,9),
    (4,2),(4,3),(4,4),(4,5),(4,6),(4,7),(4,8),(4,9),
    (6,1),(6,2),(6,3),(6,7),(6,8),(6,9),(6,10),
    (7,3),(7,9),
    (8,2),(8,3),(8,7),(8,9),
    (9,2),(9,5),(9,7),(9,9),
    (10,4),(10,5),
    (11,1),(11,2),(11,3),(11,4),(11,5),(11,6),(11,7),(11,8),(11,9),
    (12,9),
    (13,2),(13,3),(13,4),(13,5),(13,6),(13,7),(13,9),
    (14,7),
}

_SPAWN_BY_DIR = {
    "west":  (1, 5),
    "east":  (14, 5),
    "north": (7, 1),
    "south": (7, 10),
}

# ======================
# MODULE STATE
# ======================
_solved           = False
_switch_pulled    = False
_controls_inverted = False
_step_count       = 0   # local step count for inversion logic
_spawn_col        = 1
_spawn_row        = 5

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
    """Call when entering the room so spawn matches the entry door."""
    global _spawn_col, _spawn_row, _controls_inverted, _step_count
    pos = _SPAWN_BY_DIR.get(prev_dir, (1, 5))
    _spawn_col, _spawn_row = pos
    _controls_inverted = False
    _step_count = 0

def set_solved(solved):
    global _solved, _switch_pulled, _controls_inverted, _step_count
    _solved           = solved
    _switch_pulled    = False
    _controls_inverted = False
    _step_count       = 0

def get_controls_inverted():
    """main.py calls this to know whether to flip movement direction."""
    return _controls_inverted

def on_move():
    """
    Call once per successful player step in main.py.
    Updates inversion state and shows notification on flip.
    """
    global _step_count, _controls_inverted
    _step_count += 1
    was_inverted = _controls_inverted
    _controls_inverted = (_step_count // 10) % 2 == 1
    #if _controls_inverted != was_inverted:
        #_show_notify("Controls INVERTED!" if _controls_inverted else "Controls back to NORMAL!")

def try_lever(col, row, sfx = None):
    """Called by main.py on SPACE press with exact gus position."""
    global _switch_pulled, _solved
    if (col, row) == SWITCH_POS and not _switch_pulled:
        _switch_pulled = True
        _solved        = True
        #_show_notify("Lever pulled! East door is open!")

def step_on(col, row):
    """
    Called by main.py when gus lands on a tile.
    Returns (spawn_col, spawn_row) to respawn on lava, else None.
    """
    if (col, row) in LAVA_TILES:
        #_show_notify("Burned! Back to the start.")
        return (_spawn_col, _spawn_row)
    return None

def render(surface, hitbox, interact, tile_size):
    """Called once per frame by main.py."""
    _load_assets(tile_size)
    font = _assets["font"]
    sw, sh = surface.get_width(), surface.get_height()

    # Draw lava tiles
    for col, row in LAVA_TILES:
        rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
        surface.blit(_assets["lava"], rect)

    # Draw switch
    sc, sr = SWITCH_POS
    rect = pygame.Rect(sc * tile_size, sr * tile_size, tile_size, tile_size)
    state = "lever_on" if _switch_pulled else "lever_off"
    surface.blit(_assets[state], rect)

    # HUD — controls state
    steps_until_flip = 10 - (_step_count % 10)
    if _controls_inverted:
        ctrl_color = (255, 80, 80)
        ctrl_label = f"INVERTED  (flips in {steps_until_flip})"
    else:
        ctrl_color = (80, 255, 120)
        ctrl_label = f"NORMAL  (flips in {steps_until_flip})"
    ctrl_surf = font.render(ctrl_label, True, ctrl_color)
    surface.blit(ctrl_surf, (sw - ctrl_surf.get_width() - 10, sh - 30))

    # Lever prompt
    pc = hitbox.centerx // tile_size
    pr = hitbox.centery // tile_size
    if (pc, pr) == SWITCH_POS and not _switch_pulled:
        p = font.render("Press SPACE to pull the lever", True, (255, 255, 200))
        surface.blit(p, (sw // 2 - p.get_width() // 2, sh - 55))

    _draw_notify(surface, font, sw)

# ======================
# GRID EXPORT
# ======================
T_WALL = 1
T_SAFE = 3
T_LAVA = 4

def make_grid(next_dir, prev_dir, grid_cols=16, grid_rows=12):
    g = [[T_WALL] * grid_cols for _ in range(grid_rows)]
    for row in range(1, grid_rows - 1):
        for col in range(1, grid_cols - 1):
            g[row][col] = T_SAFE
    for col, row in LAVA_TILES:
        if 0 <= row < grid_rows and 0 <= col < grid_cols:
            g[row][col] = T_LAVA
    # Always open west and east gaps
    g[5][0] = T_SAFE; g[6][0] = T_SAFE
    g[5][grid_cols-1] = T_SAFE; g[6][grid_cols-1] = T_SAFE
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
    _assets["lever_off"] = img("assets/MountedLeverRightOff.png", alpha=True)
    _assets["lever_on"]  = img("assets/MountedLeverRightOn.png",  alpha=True)
    _assets["font"]      = pygame.font.Font(None, 20)
    # Build lava surface
    lava = pygame.Surface((tile_size, tile_size))
    lava.fill((220, 90, 10))
    gap = max(4, tile_size // 8)
    for i in range(0, tile_size, gap):
        pygame.draw.line(lava, (255, 160, 40), (i, 0), (i + tile_size // 2, tile_size), max(1, 2))
    _assets["lava"] = lava

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