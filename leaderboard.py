
import os
import json
import math
import datetime
import pygame


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
MAX_ENTRIES  = 10
JSON_FILENAME = "leaderboard.json"

# Screen dimensions — must match the rest of the game
TILE_SIZE = 32
SCALE     = 2
SCREEN_W  = 16 * TILE_SIZE * SCALE   # 1024
SCREEN_H  = 12 * TILE_SIZE * SCALE   # 768

# ─────────────────────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────────────────────
C_BG          = (20,  10,  35)      # deep background
C_OVERLAY     = (0,   0,   0, 160)  # vignette overlay
C_PANEL       = (30,  20,  55)      # table panel fill
C_PANEL_EDGE  = (90,  60, 160)      # panel border

C_GOLD        = (255, 210,  50)     # rank 1
C_SILVER      = (200, 200, 210)     # rank 2
C_BRONZE      = (200, 130,  60)     # rank 3
C_ROW_NORMAL  = (200, 185, 235)     # ranks 4-10
C_ROW_ALT     = (170, 155, 205)     # alternating row shade
C_HIGHLIGHT   = (255, 255, 255, 30) # hover glow on rows
C_HEADER      = (140, 110, 220)     # column header text
C_DIVIDER     = (70,  50, 110)      # horizontal rule

C_BTN_IDLE    = (55,  40,  90)
C_BTN_HOVER   = (100, 75, 175)
C_BTN_BORDER  = (130, 100, 220)
C_BTN_TEXT    = (255, 255, 255)

C_EMPTY       = (80,  65, 120)      # "no entries yet" text
C_STAR_DIM    = (60,  40, 100)      # decorative bg stars
C_SUBTITLE    = (160, 140, 210)


class LeaderboardManager:
    """
    Manages reading, writing, and rendering the leaderboard.

    Parameters
    ----------
    screen : pygame.Surface or None
        Pass the display surface here, or leave None and supply it each
        time you call  draw(screen).
    """

    def __init__(self, screen: pygame.Surface | None = None) -> None:
        self._screen = screen

        # Anchor data file next to this script
        self._base_dir  = os.path.dirname(os.path.abspath(__file__))
        self._json_path = os.path.join(self._base_dir, JSON_FILENAME)

        # Load or create the data file
        self._entries: list[dict] = []
        self._load()

        # ── Fonts ─────────────────────────────────────────────────────────
        self._font_title  = self._safe_font(None, 62)
        self._font_header = self._safe_font(None, 26)
        self._font_row    = self._safe_font(None, 28)
        self._font_btn    = self._safe_font(None, 32)
        self._font_empty  = self._safe_font(None, 26)

        # ── Back button geometry ───────────────────────────────────────────
        self._btn_w = 200
        self._btn_h = 52

        # ── Table layout ───────────────────────────────────────────────────
        self._table_x     = SCREEN_W // 2 - 380
        self._table_w     = 760
        self._row_h       = 44
        self._header_h    = 40
        self._table_top   = 120    # y of first column header
        self._col_rank    = self._table_x + 30
        self._col_name    = self._table_x + 110
        self._col_steps   = self._table_x + 530
        self._col_date    = self._table_x + 630

        # ── Tick counter for animations ────────────────────────────────────
        self._tick = 0

        # ── Button hover tracking ──────────────────────────────────────────
        self._held = False

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def submit(self, name: str, steps: int) -> bool:
        """
        Add a new completion attempt.

        Parameters
        ----------
        name  : player name string (truncated to 18 chars)
        steps : number of steps taken

        Returns True if the score made the top-10, False otherwise.
        """
        name = str(name).strip()[:18] or "Anonymous"
        entry = {
            "name":  name,
            "steps": int(steps),
            "date":  datetime.date.today().isoformat(),
        }
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e["steps"])
        self._entries = self._entries[:MAX_ENTRIES]
        self._rebuild_ranks()
        self._save()

        made_board = any(e["name"] == name and e["steps"] == steps
                         for e in self._entries)
        return made_board

    def draw(self, screen: pygame.Surface | None = None) -> str | None:
        """
        Render the leaderboard screen and handle events.

        Returns "BACK" when the back button is clicked, otherwise None.
        Call this every frame while in the LEADERBOARD state.
        """
        surf = screen or self._screen
        if surf is None:
            raise RuntimeError("No screen surface supplied to LeaderboardManager.draw()")

        self._tick += 1
        self._draw_background(surf)
        self._draw_title(surf)
        self._draw_table(surf)
        self._draw_back_button(surf)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "BACK"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._back_rect(surf).collidepoint(event.pos):
                    self._held = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                was_held = self._held
                self._held = False
                if was_held and self._back_rect(surf).collidepoint(event.pos):
                    return "BACK"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return "BACK"

        return None

    def is_high_score(self, steps: int) -> bool:
        """Returns True if `steps` would place in the current top 10."""
        if len(self._entries) < MAX_ENTRIES:
            return True
        return steps < self._entries[-1]["steps"]

    def get_entries(self) -> list[dict]:
        """Return a copy of the current leaderboard entries."""
        return list(self._entries)

    # ─────────────────────────────────────────────────────────────────────────
    # JSON persistence
    # ─────────────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load entries from JSON; creates a blank file if missing."""
        if not os.path.exists(self._json_path):
            self._entries = []
            self._save()
            print(f"[Leaderboard] Created new data file: {self._json_path}")
            return
        try:
            with open(self._json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw = data.get("entries", [])
            # Validate each entry has required keys
            self._entries = [
                e for e in raw
                if isinstance(e, dict)
                and "name"  in e
                and "steps" in e
                and "date"  in e
            ]
            for item in self._entries:
                if item["date"] != datetime.date.today().isoformat():
                    self._entries.remove(item)
            self._entries.sort(key=lambda e: e["steps"])
            self._entries = self._entries[:MAX_ENTRIES]
            self._rebuild_ranks()
            print(f"[Leaderboard] Loaded {len(self._entries)} entries.")
        except (json.JSONDecodeError, OSError) as err:
            print(f"[Leaderboard] WARNING — could not read {self._json_path}: {err}")
            self._entries = []

    def _save(self) -> None:
        """Write current entries to JSON."""
        data = {"entries": self._entries}
        try:
            with open(self._json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as err:
            print(f"[Leaderboard] WARNING — could not save: {err}")

    def _rebuild_ranks(self) -> None:
        """Re-assign 1-based rank field after any sort."""
        for i, entry in enumerate(self._entries):
            entry["rank"] = i + 1

    # ─────────────────────────────────────────────────────────────────────────
    # Drawing helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _draw_background(self, surf: pygame.Surface) -> None:
        surf.fill(C_BG)

        # Decorative background stars
        positions = [
            (60, 50), (200, 30), (400, 80), (700, 40), (950, 70),
            (30, 300), (990, 250), (100, 600), (900, 550), (500, 720),
            (150, 720), (800, 700), (350, 50), (600, 730),
        ]
        pulse = abs(math.sin(self._tick * 0.025))
        for sx, sy in positions:
            b = int(40 + 40 * pulse)
            pygame.draw.circle(surf, (b, b - 10, b + 20), (sx, sy), 2)

        # Vignette
        for i in range(5):
            radius = int(SCREEN_W * 0.62) - i * 50
            v = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.ellipse(
                v, (0, 0, 0, 22),
                pygame.Rect(
                    SCREEN_W // 2 - radius, SCREEN_H // 2 - radius,
                    radius * 2, radius * 2,
                ),
            )
            surf.blit(v, (0, 0))

    def _draw_title(self, surf: pygame.Surface) -> None:
        # Glow layers for title text
        title = "LEADERBOARD"
        glow_colors = [
            ((120, 80, 200), 7),
            ((140, 95, 220), 5),
            ((160, 110, 240), 3),
        ]
        for (gc, offset) in glow_colors:
            for ox in (-offset, 0, offset):
                for oy in (-offset, 0, offset):
                    if ox == 0 and oy == 0:
                        continue
                    gs = self._font_title.render(title, True, gc)
                    gr = gs.get_rect(centerx=SCREEN_W // 2 + ox, y=48 + oy)
                    surf.blit(gs, gr)

        # Main title
        ts = self._font_title.render(title, True, C_GOLD)
        tr = ts.get_rect(centerx=SCREEN_W // 2, y=48)
        surf.blit(ts, tr)

    def _draw_table(self, surf: pygame.Surface) -> None:
        tx = self._table_x
        tw = self._table_w
        th = self._header_h + self._row_h * MAX_ENTRIES
        ty = self._table_top

        # Panel background
        panel = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*C_PANEL, 210), (0, 0, tw, th), border_radius=14)
        pygame.draw.rect(panel, C_PANEL_EDGE,    (0, 0, tw, th), width=2, border_radius=14)
        surf.blit(panel, (tx, ty))

        # Column headers
        headers = [
            (self._col_rank  - tx, "#"),
            (self._col_name  - tx, "PLAYER"),
            (self._col_steps - tx, "STEPS"),
            (self._col_date  - tx, "DATE"),
        ]
        hy = ty + 10
        for hx_local, label in headers:
            hs = self._font_header.render(label, True, C_HEADER)
            surf.blit(hs, (tx + hx_local, hy))

        # Divider under headers
        div_y = ty + self._header_h
        pygame.draw.line(surf, C_PANEL_EDGE,
                         (tx + 10, div_y), (tx + tw - 10, div_y), 1)

        # ── Rows ──────────────────────────────────────────────────────────
        mouse_pos = pygame.mouse.get_pos()

        for slot in range(MAX_ENTRIES):
            row_y = div_y + slot * self._row_h

            # Alternating row shading
            if slot % 2 == 0:
                row_surf = pygame.Surface((tw - 4, self._row_h), pygame.SRCALPHA)
                row_surf.fill((255, 255, 255, 8))
                surf.blit(row_surf, (tx + 2, row_y))

            # Mouse hover highlight
            row_rect = pygame.Rect(tx + 2, row_y, tw - 4, self._row_h)
            if row_rect.collidepoint(mouse_pos) and slot < len(self._entries):
                hl = pygame.Surface((tw - 4, self._row_h), pygame.SRCALPHA)
                hl.fill(C_HIGHLIGHT)
                surf.blit(hl, (tx + 2, row_y))

            text_y = row_y + (self._row_h - self._font_row.get_height()) // 2

            if slot < len(self._entries):
                entry = self._entries[slot]
                rank  = entry["rank"]

                # Rank colour
                if   rank == 1: rc = C_GOLD
                elif rank == 2: rc = C_SILVER
                elif rank == 3: rc = C_BRONZE
                else:           rc = C_ROW_NORMAL

                # Rank number — always shown, colour identifies top 3
                rs = self._font_row.render(str(rank), True, rc)
                surf.blit(rs, (self._col_rank, text_y))

                # Name
                ns = self._font_row.render(entry["name"], True, rc)
                surf.blit(ns, (self._col_name, text_y))

                # Steps — bold for top 3
                step_text = str(entry["steps"])
                ss = self._font_row.render(step_text, True, rc)
                surf.blit(ss, (self._col_steps, text_y))

                # Date
                ds = self._font_empty.render(entry["date"], True, C_SUBTITLE)
                surf.blit(ds, (self._col_date, text_y))

            else:
                # Empty slot — still show the rank number
                es = self._font_empty.render(str(slot + 1), True, C_EMPTY)
                surf.blit(es, (self._col_rank, text_y))
                ph = self._font_empty.render("Not yet claimed", True, C_EMPTY)
                surf.blit(ph, (self._col_name, text_y))

            # Row divider
            if slot < MAX_ENTRIES - 1:
                line_y = row_y + self._row_h
                pygame.draw.line(surf, C_DIVIDER,
                                 (tx + 10, line_y), (tx + tw - 10, line_y), 1)

    def _back_rect(self, surf: pygame.Surface) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_W // 2 - self._btn_w // 2,
            SCREEN_H - 80,
            self._btn_w,
            self._btn_h,
        )

    def _draw_back_button(self, surf: pygame.Surface) -> None:
        rect      = self._back_rect(surf)
        mouse_pos = pygame.mouse.get_pos()
        hovered   = rect.collidepoint(mouse_pos)
        held      = self._held and hovered

        color  = C_BTN_HOVER if (hovered or held) else C_BTN_IDLE
        border = C_BTN_TEXT  if (hovered or held) else C_BTN_BORDER

        # Shadow
        shadow = rect.move(4, 4)
        sh = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        sh.fill((0, 0, 0, 60))
        surf.blit(sh, shadow.topleft)

        pygame.draw.rect(surf, color,  rect, border_radius=10)
        pygame.draw.rect(surf, border, rect, width=2, border_radius=10)

        label = "← BACK"
        ls = self._font_btn.render(label, True, C_BTN_TEXT)
        surf.blit(ls, ls.get_rect(center=rect.center))

    @staticmethod
    def _safe_font(name, size):
        try:
            return pygame.font.SysFont(name, size, bold=True)
        except Exception:
            return pygame.font.Font(None, size)


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test  (run:  python leaderboard.py)
# Populates the board with dummy data so you can see the layout immediately.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Leaderboard Test")
    clock = pygame.time.Clock()

    lb = LeaderboardManager(screen)

    # Seed dummy data if the board is empty
    if not lb.get_entries():
        test_data = [
            ("Samrat",   42),
            ("Alex",     58),
            ("Jordan",   63),
            ("Taylor",   71),
            ("Morgan",   85),
            ("Casey",    92),
            ("Riley",   104),
            ("Quinn",   117),
            ("Avery",   133),
            ("Blake",   150),
        ]
        for name, steps in test_data:
            lb.submit(name, steps)
        print("[Test] Seeded 10 dummy entries.")

    running = True
    while running:
        clock.tick(60)
        action = lb.draw(screen)
        if action == "BACK":
            print("[Test] BACK pressed — exiting.")
            running = False
        pygame.display.flip()

    pygame.quit()
