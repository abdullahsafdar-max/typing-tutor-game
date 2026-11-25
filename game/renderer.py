"""
renderer.py
Draws everything on the screen. It only DRAWS; it never decides game rules.
"""

import math

import pygame

import config


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        # Fonts must be created AFTER pygame.init() (Game does that first)
        self.font_title = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_TITLE, bold=True)
        self.font_button = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_BUTTON, bold=True)
        self.font_hud = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_HUD)
        self.font_hud_bold = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_HUD, bold=True)
        self.font_small = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_SMALL)

        # The big card in the middle of the menu
        self.card_rect = pygame.Rect(0, 0, 760, 520)
        self.card_rect.center = (config.WINDOW_WIDTH // 2, 350)

        # The Start Game button. Game.py uses this rectangle to detect mouse clicks.
        self.start_button_rect = pygame.Rect(0, 0, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
        self.start_button_rect.center = (config.WINDOW_WIDTH // 2, 350)

    # ------------------------------------------------------------
    # Small helper
    # ------------------------------------------------------------
    def _draw_text(self, text, font, color, **position):
        """Draw text. Give a position like center=(x, y), topleft=(x, y) or topright=(x, y)."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(**position)
        self.screen.blit(surface, rect)
        return rect

    # ------------------------------------------------------------
    # MENU screen
    # ------------------------------------------------------------
    def draw_menu(self, mouse_pos):
        center_x = config.WINDOW_WIDTH // 2
        self.screen.fill(config.COLOR_BACKGROUND)

        # Card with a thin border
        pygame.draw.rect(self.screen, config.COLOR_PLAY_AREA, self.card_rect, border_radius=24)
        pygame.draw.rect(self.screen, config.COLOR_CARD_BORDER, self.card_rect, width=2, border_radius=24)

        # Title and subtitle
        self._draw_text("Typing Tutor", self.font_title, config.COLOR_TEXT, center=(center_x, 175))
        self._draw_text("Type each falling character before it reaches the Dead Bar",
                        self.font_hud, config.COLOR_TEXT_DIM, center=(center_x, 240))

        # Start Game button (lighter color when the mouse is over it)
        if self.start_button_rect.collidepoint(mouse_pos):
            button_color = config.COLOR_ACCENT_HOVER
        else:
            button_color = config.COLOR_ACCENT
        pygame.draw.rect(self.screen, button_color, self.start_button_rect,
                         border_radius=config.BUTTON_RADIUS)
        self._draw_text("Start Game", self.font_button, config.COLOR_TEXT,
                        center=self.start_button_rect.center)
        self._draw_text("Click the button or press ENTER", self.font_small,
                        config.COLOR_TEXT_DIM, center=(center_x, 410))

        # Thin divider line
        line_y = 465
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER,
                         (self.card_rect.left + 60, line_y), (self.card_rect.right - 60, line_y), 2)

        # Color legend: what each color means
        self._draw_text("CHARACTER COLORS", self.font_small, config.COLOR_TEXT_DIM,
                        center=(center_x, 495))
        self._draw_legend_item("a-z", config.COLOR_LOWERCASE, "lowercase", center_x - 230, 545)
        self._draw_legend_item("A-Z", config.COLOR_UPPERCASE, "uppercase", center_x, 545)
        self._draw_legend_item("0-9", config.COLOR_DIGIT, "digits", center_x + 230, 545)

        # Key hints below the card
        self._draw_text("ENTER  Start        ESC  Exit", self.font_small,
                        config.COLOR_TEXT_DIM, center=(center_x, 650))

    def _draw_legend_item(self, sample, color, label, center_x, y):
        """Draw a colored sample (like 'a-z') followed by a small label, centered as a group."""
        sample_surface = self.font_hud_bold.render(sample, True, color)
        label_surface = self.font_small.render(label, True, config.COLOR_TEXT_DIM)
        gap = 10
        total_width = sample_surface.get_width() + gap + label_surface.get_width()
        left = center_x - total_width // 2
        self.screen.blit(sample_surface, sample_surface.get_rect(midleft=(left, y)))
        self.screen.blit(label_surface,
                         label_surface.get_rect(midleft=(left + sample_surface.get_width() + gap, y)))

    # ------------------------------------------------------------
    # PLAYING screen (temporary version for Milestone 5)
    # ------------------------------------------------------------
    def draw_playing(self, stats):
        self.screen.fill(config.COLOR_BACKGROUND)

        # Left: play area
        play_rect = pygame.Rect(0, 0, config.PLAY_AREA_WIDTH, config.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PLAY_AREA, play_rect)

        # Dead Bar
        dead_bar_rect = pygame.Rect(0, config.DEAD_BAR_Y, config.PLAY_AREA_WIDTH,
                                    config.DEAD_BAR_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_DEAD_BAR, dead_bar_rect)
        self._draw_text("DEAD BAR", self.font_small, config.COLOR_DEAD_BAR,
                        topleft=(20, config.DEAD_BAR_Y + 14))

        # Temporary message in the middle of the play area
        middle_x = config.PLAY_AREA_WIDTH // 2
        self._draw_text("Get ready!", self.font_title, config.COLOR_TEXT, center=(middle_x, 280))
        self._draw_text("Falling characters will appear here in the next milestone.",
                        self.font_hud, config.COLOR_TEXT_DIM, center=(middle_x, 345))

        # Right: stats panel
        panel_x = config.PLAY_AREA_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, config.PANEL_WIDTH, config.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PANEL, panel_rect)
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER,
                         (panel_x, 0), (panel_x, config.WINDOW_HEIGHT), 2)

        left = panel_x + 24
        right = panel_x + config.PANEL_WIDTH - 24

        self._draw_text("STATS", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 28))

        # Remaining = characters in the Queue + characters falling.
        # The Queue does not exist yet (Milestone 6), so we use the full 80 for now.
        remaining = stats.get_remaining(config.TOTAL_CHARACTERS, 0)

        rows = [
            ("Time Left", self._format_time(stats.time_left)),
            ("Hits", str(stats.hits)),
            ("Misses", str(stats.misses)),
            ("Key Presses", str(stats.key_presses)),
            ("Accuracy", f"{stats.get_accuracy():.1f}%"),
            ("Remaining", str(remaining)),
        ]
        y = 75
        for label, value in rows:
            self._draw_text(label, self.font_hud, config.COLOR_TEXT_DIM, midleft=(left, y))
            self._draw_text(value, self.font_hud_bold, config.COLOR_TEXT, midright=(right, y))
            y += 46

        # Recent events (read from our Stack through GameStats)
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER, (left, 380), (right, 380), 2)
        self._draw_text("RECENT EVENTS", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 400))
        events = stats.get_recent_events(5)
        if len(events) == 0:
            self._draw_text("No events yet", self.font_small, config.COLOR_TEXT_DIM,
                            topleft=(left, 435))
        else:
            event_y = 435
            for event_text in events:
                self._draw_text(event_text, self.font_small, config.COLOR_TEXT, topleft=(left, event_y))
                event_y += 28

        # Key hint
        self._draw_text("ESC  Exit", self.font_small, config.COLOR_TEXT_DIM,
                        bottomleft=(left, config.WINDOW_HEIGHT - 24))

    @staticmethod
    def _format_time(seconds):
        """Turn seconds into mm:ss. Example: 60 -> '01:00'."""
        whole_seconds = int(math.ceil(seconds))
        minutes = whole_seconds // 60
        secs = whole_seconds % 60
        return f"{minutes:02d}:{secs:02d}"