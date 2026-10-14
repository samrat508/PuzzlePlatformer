"""
NoBacktrackRoom.py — puzzle room module for main.py
Interface:
    render(surface, hitbox, interact, tile_size)
    get_solved() -> bool
    set_solved(bool)
    make_grid(next_dir, prev_dir, grid_cols, grid_rows) -> grid
    on_move(next_col, next_row) -> extra_steps (int)
        Called in main.py's movement block with the destination tile (nc, nr).
        Returns 1 if revisit penalty applies, else 0.
"""
import pygame


ROCK_TILES = {
    (4, 5),
    (8, 4),
    (6, 5),
    (10, 3),
    (5, 7),
    (9, 6),
    (10, 8),
}

PUZZLE_COL_START = 3
PUZZLE_COL_END   = 12
PUZZLE_ROW_START = 3
PUZZLE_ROW_END   = 8

# ======================
# MODULE STATE
# ======================
_solved           = False
_designated_tiles = set()
_visited          = set()

_notify_text  = ""
_notify_timer = 0
NOTIFY_DURATION = 2000

_assets      = {}
_cached_grid = None

# ======================
# PUBLIC API
# ======================
def get_solved():
    return _solved

def set_solved(solved):
    global _solved, _visited, _cached_grid
    _solved      = solved
    _visited     = set()
    _cached_grid = None   # force grid rebuild on next entry

def on_move(next_col, next_row):
    """
    Called in main.py's movement block with the tile the player is moving TO.
    Fires exactly once per keypress — correct place to track visits and penalty.
    Returns extra steps to add (0 normally, 1 on revisit).
    """
    global _solved, _visited
    pos = (next_col, next_row)

    if pos not in _designated_tiles:
        return 0

    if pos in _visited:
        #_show_notify("Revisit! +1 step penalty.")
        return 1   # penalty — already visited
    else:
        _visited.add(pos)
        remaining = len(_designated_tiles) - len(_visited)
        if remaining == 0:
            _solved = True
        # if remaining > 0:
        #     #_show_notify(f"Tile found! {remaining} left.")
        # else:
        #     _solved = True
        #     #_show_notify("All tiles found! Door unlocked.")
        return 0

def render(surface, hitbox, interact, tile_size):
    """Called once per frame by main.py."""
    _load_assets(tile_size)
    font = _assets["font"]
    sw, sh = surface.get_width(), surface.get_height()

    # Green overlay on visited tiles
    for col, row in _visited:
        rect    = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
        overlay = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        overlay.fill((0, 255, 0, 100))
        surface.blit(overlay, rect)

    # Progress HUD
    total   = len(_designated_tiles)
    visited = len(_visited)
    prog = font.render(f"Tiles: {visited} / {total}", True, (220, 220, 80))
    surface.blit(prog, (sw // 2 - prog.get_width() // 2, sh - 30))

    _draw_notify(surface, font, sw)

# ======================
# GRID EXPORT
# ======================
T_WALL = 1
T_ROCK = 2
T_SAFE = 3

def make_grid(next_dir, prev_dir, grid_cols=16, grid_rows=12):
    global _designated_tiles, _cached_grid

    # Return cached grid — prevents any per-frame rebuilding
    if _cached_grid is not None:
        return _cached_grid

    g = [[T_WALL] * grid_cols for _ in range(grid_rows)]
    for row in range(1, grid_rows - 1):
        for col in range(1, grid_cols - 1):
            g[row][col] = T_SAFE

    # Rock surround around puzzle area
    for col in range(2, 14):
        g[2][col] = T_ROCK
        g[9][col] = T_ROCK
    for row in range(3, 9):
        g[row][2]  = T_ROCK
        g[row][13] = T_ROCK

    # Entryways through rock surround
    g[5][2] = T_SAFE;  g[6][2] = T_SAFE
    g[5][13] = T_SAFE; g[6][13] = T_SAFE
    g[2][7] = T_SAFE;  g[2][8] = T_SAFE
    g[9][7] = T_SAFE;  g[9][8] = T_SAFE

    # Fixed rocks inside puzzle area
    for col, row in ROCK_TILES:
        if 0 <= row < grid_rows and 0 <= col < grid_cols:
            g[row][col] = T_ROCK

    # Door gaps from navigation directions
    g[5][0] = T_SAFE; g[6][0] = T_SAFE
    g[5][grid_cols-1] = T_SAFE; g[6][grid_cols-1] = T_SAFE
    if next_dir == "north" or prev_dir == "north": g[0][7] = T_SAFE; g[0][8] = T_SAFE
    if next_dir == "south" or prev_dir == "south": g[grid_rows-1][7] = T_SAFE; g[grid_rows-1][8] = T_SAFE

    # Collect designated tiles — all safe tiles inside the puzzle area
    _designated_tiles = {
        (col, row)
        for row in range(PUZZLE_ROW_START, PUZZLE_ROW_END + 1)
        for col in range(PUZZLE_COL_START, PUZZLE_COL_END + 1)
        if g[row][col] == T_SAFE
    }

    _cached_grid = g
    return g

# ======================
# INTERNAL HELPERS
# ======================
def _load_assets(tile_size):
    if _assets:
        return
    _assets["font"] = pygame.font.Font(None, 20)

def _show_notify(text):
    global _notify_text, _notify_timer
    _notify_text  = text
    _notify_timer = pygame.time.get_ticks()

def _draw_notify(surface, font, screen_width):
    if _notify_text and pygame.time.get_ticks() - _notify_timer < NOTIFY_DURATION:
        txt = font.render(_notify_text, True, (255, 255, 255))
        bg  = pygame.Surface((txt.get_width()+10, txt.get_height()+6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg,  (screen_width//2 - bg.get_width()//2,  17))
        surface.blit(txt, (screen_width//2 - txt.get_width()//2, 20))