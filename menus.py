

import os
import math
import pygame


# ─────────────────────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────────────────────
COLOR_BG_DARK      = (65,  12,  65)
COLOR_OVERLAY      = (0,   0,   0,  160)
COLOR_PANEL        = (28,  22,  48)
COLOR_PANEL_BORDER = (90,  70, 160)
COLOR_SUBTITLE     = (200, 180, 255)
COLOR_STAR         = (255, 230,  80)


# ─────────────────────────────────────────────────────────────────────────────
# MenuManager
# ─────────────────────────────────────────────────────────────────────────────
class MenuManager:

    TILE_SIZE = 32
    SCALE     = 2
    TILES_X   = 16
    TILES_Y   = 12
    SCREEN_W  = TILE_SIZE * TILES_X * SCALE   # 1024
    SCREEN_H  = TILE_SIZE * TILES_Y * SCALE   # 768

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        # ── Header images ─────────────────────────────────────────────────
        self.title_img  = pygame.image.load('assets/TitleV3.png').convert_alpha()
        self.paused_img = pygame.image.load('assets/Paused.png').convert_alpha()
        self.victory_img = pygame.image.load('assets/Victory.png').convert_alpha()

        # ── Button sets: [normal, hover, clicked] ─────────────────────────
        self.start_imgs = [
            pygame.image.load('assets/StartButton1.png').convert_alpha(),
            pygame.image.load('assets/StartButton2.png').convert_alpha(),
            pygame.image.load('assets/StartButton3.png').convert_alpha(),
        ]
        self.resume_imgs = [
            pygame.image.load('assets/ResumeButton1.png').convert_alpha(),
            pygame.image.load('assets/ResumeButton2.png').convert_alpha(),
            pygame.image.load('assets/ResumeButton3.png').convert_alpha(),
        ]
        self.quit_imgs = [
            pygame.image.load('assets/QuitButton1.png').convert_alpha(),
            pygame.image.load('assets/QuitButton2.png').convert_alpha(),
            pygame.image.load('assets/QuitButton3.png').convert_alpha(),
        ]
        self.leaderboard_imgs = [
            pygame.image.load('assets/LeaderboardButton1.png').convert_alpha(),
            pygame.image.load('assets/LeaderboardButton2.png').convert_alpha(),
            pygame.image.load('assets/LeaderboardButton3.png').convert_alpha(),
        ]

        # ── Fonts ─────────────────────────────────────────────────────────
        self._font_small = self._load_font(None, 22)

        # ── Overlay for pause dimming ──────────────────────────────────────
        self._overlay = pygame.Surface(
            (self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA
        )
        self._overlay.fill(COLOR_OVERLAY)

        # ── Pre-render the glowing title border surface once ───────────────
        # This avoids rebuilding it every frame — it never changes.
        self._title_surface = self._build_title_surface()

        # ── Button sizes ──────────────────────────────────────────────────
        self._btn_w = 260
        self._btn_h = 60

        # ── Animation tick ────────────────────────────────────────────────
        self._tick = 0

        # ── Currently held button id ──────────────────────────────────────
        self._held_button = None

    # ─────────────────────────────────────────────────────────────────────────
    # Title glow builder  (called once in __init__)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_title_surface(self) -> pygame.Surface | None:
        """
        Composites the title image onto a glow-ring background.
        Returns a ready-to-blit Surface, or None if title_img is missing.

        How the glow works:
          - We draw several concentric ellipses from outermost to innermost,
            each slightly brighter and slightly smaller.
          - This creates a smooth bloom effect without needing any shader.
          - The title image is blitted on top, centred inside the rings.
        """
        if not self.title_img:
            return None

        img_w = self.title_img.get_width()
        img_h = self.title_img.get_height()

        # How much larger the glow extends beyond the image on each side
        GLOW_PAD = 48

        surf_w = img_w + GLOW_PAD * 2
        surf_h = img_h + GLOW_PAD * 2
        surf   = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        # ── Glow rings: outermost (dark/dim) → innermost (near white) ──────
        # Each entry: (shrink amount from edge, RGB colour, alpha, stroke width)
        glow_layers = [
            (0,   ( 80,   0,  82),  30,  20),   # outermost — very dim purple halo
            (6,   ( 95,   0,  98),  50,  17),
            (12,  (110,   0, 113),  70,  15),
            (18,  (130,   0, 133),  95,  13),
            (24,  (150,  10, 150), 120,  11),
            (30,  (170,  30, 170), 148,   9),
            (36,  (190,  60, 190), 170,   7),
            (42,  (210,  90, 210), 190,   5),
            (47,  (230, 140, 230), 210,   4),
            (52,  (245, 190, 245), 225,   3),
            (56,  (255, 230, 255), 240,   2),   # innermost — near white
        ]

        full_rect = pygame.Rect(0, 0, surf_w, surf_h)

        for shrink, rgb, alpha, stroke in glow_layers:
            layer = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            r = pygame.Rect(
                shrink, shrink,
                surf_w - shrink * 2,
                surf_h - shrink * 2,
            )
            pygame.draw.ellipse(layer, (*rgb, alpha), r, stroke)
            surf.blit(layer, (0, 0))

        # ── Title image centred inside the glow ───────────────────────────
        surf.blit(self.title_img, (GLOW_PAD, GLOW_PAD))

        return surf

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def draw_start_menu(self) -> str | None:
        """Returns "START", "QUIT", "LEADERBOARD", or None."""
        self._tick += 1
        self._draw_background()
        self._draw_stars_decoration()

        # ── Title with glow ───────────────────────────────────────────────
        if self._title_surface:
            rect = self._title_surface.get_rect(
                centerx=self.SCREEN_W // 2,
                centery=self.SCREEN_H // 2 - 170,
            )
            self.screen.blit(self._title_surface, rect)
        else:
            self._draw_text_centered(
                "MY GAME", self._font_small,
                (255, 230, 100), y=self.SCREEN_H // 2 - 200,
            )

        # ── Buttons: Start / Leaderboard / Quit stacked vertically ────────
        cx           = self.SCREEN_W // 2
        start_rect   = self._btn_rect(cx, self.SCREEN_H // 2 + 20)
        leader_rect  = self._btn_rect(cx, self.SCREEN_H // 2 + 100)
        quit_rect    = self._btn_rect(cx, self.SCREEN_H // 2 + 180)
        mouse_pos    = pygame.mouse.get_pos()

        self._draw_image_button(start_rect,  self.start_imgs,       mouse_pos, "start")
        self._draw_image_button(leader_rect, self.leaderboard_imgs, mouse_pos, "leaderboard")
        self._draw_image_button(quit_rect,   self.quit_imgs,        mouse_pos, "quit")


        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    self._held_button = "start"
                elif leader_rect.collidepoint(event.pos):
                    self._held_button = "leaderboard"
                elif quit_rect.collidepoint(event.pos):
                    self._held_button = "quit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                released_on = self._held_button
                self._held_button = None
                if released_on == "start"       and start_rect.collidepoint(event.pos):
                    return "START"
                if released_on == "leaderboard" and leader_rect.collidepoint(event.pos):
                    return "LEADERBOARD"
                if released_on == "quit"        and quit_rect.collidepoint(event.pos):
                    return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "START"
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "QUIT"

        return None

    # ─────────────────────────────────────────────────────────────────────────

    def draw_pause_menu(self) -> str | None:
        """Returns "RESUME", "QUIT", or None."""
        self._tick += 1

        self.screen.blit(self._overlay, (0, 0))

        panel_w, panel_h = 400, 300
        panel_x = (self.SCREEN_W - panel_w) // 2
        panel_y = (self.SCREEN_H - panel_h) // 2
        self._draw_panel(panel_x, panel_y, panel_w, panel_h)

        # ── Paused header image (no subtitle text beneath it) ─────────────
        if self.paused_img:
            p_rect = self.paused_img.get_rect(
                centerx=self.SCREEN_W // 2,
                y=panel_y + 20,
            )
            self.screen.blit(self.paused_img, p_rect)
        else:
            self._draw_text_centered(
                "PAUSED", self._font_small,
                (255, 230, 100), y=panel_y + 40,
            )

        # ── Buttons — moved up slightly since subtitle text is removed ────
        cx          = self.SCREEN_W // 2
        resume_rect = self._btn_rect(cx, panel_y + 170)
        quit_rect   = self._btn_rect(cx, panel_y + 245)
        mouse_pos   = pygame.mouse.get_pos()

        self._draw_image_button(resume_rect, self.resume_imgs, mouse_pos, "resume")
        self._draw_image_button(quit_rect,   self.quit_imgs,   mouse_pos, "quit")

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if resume_rect.collidepoint(event.pos):
                    self._held_button = "resume"
                elif quit_rect.collidepoint(event.pos):
                    self._held_button = "quit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                released_on = self._held_button
                self._held_button = None
                if released_on == "resume" and resume_rect.collidepoint(event.pos):
                    return "RESUME"
                if released_on == "quit" and quit_rect.collidepoint(event.pos):
                    return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "RESUME"

        return None

    # ─────────────────────────────────────────────────────────────────────────

    def draw_victory_menu(self) -> str | None:
        """Returns "RETRY", "QUIT", "LEADERBOARD", or None."""
        self._tick += 1
        self._draw_background(tint=(10, 30, 15))
        self._draw_confetti()

        if self.victory_img:
            rect = self.victory_img.get_rect(
                centerx=self.SCREEN_W // 2,
                centery=self.SCREEN_H // 2 - 170,
            )
            self.screen.blit(self.victory_img, rect)
        else:
            self._draw_text_centered(
                "VICTORY!", self._font_small,
                (255, 210, 50), y=self.SCREEN_H // 2 - 170,
            )

        # ── Buttons: Try Again / Leaderboard / Quit stacked vertically ────
        cx           = self.SCREEN_W // 2
        retry_rect   = self._btn_rect(cx, self.SCREEN_H // 2 - 50)
        leader_rect  = self._btn_rect(cx, self.SCREEN_H // 2 + 30)
        quit_rect    = self._btn_rect(cx, self.SCREEN_H // 2 + 110)
        mouse_pos    = pygame.mouse.get_pos()

        self._draw_image_button(retry_rect,  self.start_imgs,       mouse_pos, "retry")
        self._draw_image_button(leader_rect, self.leaderboard_imgs, mouse_pos, "leaderboard")
        self._draw_image_button(quit_rect,   self.quit_imgs,        mouse_pos, "quit")

        # ── Events ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(event.pos):
                    self._held_button = "retry"
                elif leader_rect.collidepoint(event.pos):
                    self._held_button = "leaderboard"
                elif quit_rect.collidepoint(event.pos):
                    self._held_button = "quit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                released_on = self._held_button
                self._held_button = None
                if released_on == "retry"       and retry_rect.collidepoint(event.pos):
                    return "RETRY"
                if released_on == "leaderboard" and leader_rect.collidepoint(event.pos):
                    return "LEADERBOARD"
                if released_on == "quit"        and quit_rect.collidepoint(event.pos):
                    return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    return "RETRY"
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return "QUIT"

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _load_font(name, size):
        try:
            return pygame.font.SysFont(name, size, bold=True)
        except Exception:
            return pygame.font.Font(None, size)

    def _btn_rect(self, cx: int, cy: int) -> pygame.Rect:
        return pygame.Rect(
            cx - self._btn_w // 2,
            cy - self._btn_h // 2,
            self._btn_w,
            self._btn_h,
        )

    def _draw_image_button(self, rect, img_set, mouse_pos, button_id):
        hovered = rect.collidepoint(mouse_pos)
        held    = (self._held_button == button_id)

        if held and hovered:
            img = img_set[2]
        elif hovered:
            img = img_set[1]
        else:
            img = img_set[0]

        if img is not None:
            scaled = pygame.transform.scale(img, (rect.width, rect.height))
            self.screen.blit(scaled, rect.topleft)
        else:
            color = (100, 80, 180) if hovered else (55, 45, 90)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (130, 100, 220), rect, width=2, border_radius=10)
            surf = self._font_small.render(button_id.upper(), True, (255, 255, 255))
            self.screen.blit(surf, surf.get_rect(center=rect.center))

    def _draw_text_centered(self, text, font, color, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(centerx=self.SCREEN_W // 2, y=y)
        self.screen.blit(surf, rect)

    def _draw_background(self, tint=COLOR_BG_DARK):
        self.screen.fill(tint)
        for i in range(6):
            radius   = int(self.SCREEN_W * 0.55) - i * 40
            vignette = pygame.Surface(
                (self.SCREEN_W, self.SCREEN_H), pygame.SRCALPHA
            )
            pygame.draw.ellipse(
                vignette, (0, 0, 0, 18),
                pygame.Rect(
                    self.SCREEN_W // 2 - radius,
                    self.SCREEN_H // 2 - radius,
                    radius * 2, radius * 2,
                ),
            )
            self.screen.blit(vignette, (0, 0))

    def _draw_panel(self, x, y, w, h):
        panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surf, (*COLOR_PANEL, 220),
            pygame.Rect(0, 0, w, h), border_radius=16,
        )
        pygame.draw.rect(
            panel_surf, COLOR_PANEL_BORDER,
            pygame.Rect(0, 0, w, h), width=2, border_radius=16,
        )
        self.screen.blit(panel_surf, (x, y))

    def _draw_stars_decoration(self):
        star_positions = [
            (120, 80), (900, 60), (50, 400), (970, 350),
            (200, 650), (820, 700), (500, 50), (400, 720),
        ]
        pulse = abs(math.sin(self._tick * 0.03))
        for sx, sy in star_positions:
            brightness = int(120 + 135 * pulse)
            color = (brightness, brightness, int(brightness * 0.9))
            pygame.draw.circle(self.screen, color, (sx, sy), 3)
            pygame.draw.circle(self.screen, color, (sx, sy), 1)

    def _draw_confetti(self):
        colors = [
            (255, 80,  80),
            (80, 200, 120),
            (80, 160, 255),
            (255, 220, 50),
            (200, 80, 255),
        ]
        for i in range(40):
            x     = int((i * 97 + self._tick * 2)   % self.SCREEN_W)
            y     = int((i * 53 + self._tick * 1.5) % self.SCREEN_H)
            size  = 6 + (i % 4) * 2
            color = colors[i % len(colors)]
            if i % 2 == 0:
                pygame.draw.rect(self.screen, color, (x, y, size, size // 2))
            else:
                pygame.draw.circle(self.screen, color, (x, y), size // 2)


# ─────────────────────────────────────────────────────────────────────────────
# Quick standalone test  (run:  python menus.py)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((MenuManager.SCREEN_W, MenuManager.SCREEN_H))
    pygame.display.set_caption("Menu Test")
    clock = pygame.time.Clock()

    menu  = MenuManager(screen)
    state = "START"

    running = True
    while running:
        clock.tick(60)

        if state == "START":
            action = menu.draw_start_menu()
            if action == "START":
                print("[TEST] → PLAYING")
                state = "PLAYING"
            elif action == "LEADERBOARD":
                print("[TEST] → LEADERBOARD (hook up your leaderboard screen here)")
            elif action == "QUIT":
                running = False

        elif state == "PLAYING":
            screen.fill((20, 40, 20))
            font = pygame.font.Font(None, 48)
            surf = font.render(
                "GAME RUNNING  |  ESC = Pause  |  V = Victory",
                True, (200, 255, 200),
            )
            screen.blit(surf, surf.get_rect(center=(MenuManager.SCREEN_W // 2, MenuManager.SCREEN_H // 2)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "PAUSED"
                    if event.key == pygame.K_v:
                        state = "VICTORY"

        elif state == "PAUSED":
            action = menu.draw_pause_menu()
            if action == "RESUME":
                print("[TEST] → PLAYING")
                state = "PLAYING"
            elif action == "QUIT":
                print("[TEST] → START")
                state = "START"

        elif state == "VICTORY":
            action = menu.draw_victory_menu()
            if action == "RETRY":
                print("[TEST] → PLAYING")
                state = "PLAYING"
            elif action == "LEADERBOARD":
                print("[TEST] → LEADERBOARD (hook up your leaderboard screen here)")
            elif action == "QUIT":
                print("[TEST] → START")
                state = "START"

        pygame.display.flip()

    pygame.quit()
