"""
renderer.py
Draws everything on the screen. It only DRAWS; it never decides game rules.
"""

import math

import pygame

import config
from game.character import URGENCY_DANGER, URGENCY_WARNING
from game.game_stats import ACCURACY_FAIR, ACCURACY_GOOD, ACCURACY_NONE, ACCURACY_POOR
from game.round_manager import END_ALL_DONE


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        # Fonts must be created AFTER pygame.init() (Game does that first)
        self.font_title = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_TITLE, bold=True)
        self.font_button = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_BUTTON, bold=True)
        self.font_hud = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_HUD)
        self.font_hud_bold = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_HUD, bold=True)
        self.font_small = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_SMALL)
        self.font_timer = pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_TIMER, bold=True)
        # Falling characters use a separate font where I, l, 1, O and 0 look different
        self.font_character = pygame.font.SysFont(config.CHARACTER_FONT_NAME,
                                                  config.FONT_SIZE_CHARACTER, bold=True)

        # Color for each character category (Character.get_category gives the key)
        self.category_colors = {
            "lower": config.COLOR_LOWERCASE,
            "upper": config.COLOR_UPPERCASE,
            "digit": config.COLOR_DIGIT,
        }

        # Outline color for each urgency level (Character.get_urgency_level gives the key)
        self.urgency_colors = {
            URGENCY_WARNING: config.COLOR_URGENCY_WARNING,
            URGENCY_DANGER: config.COLOR_URGENCY_DANGER,
        }

        # Color for each accuracy level (GameStats.get_accuracy_level gives the key)
        self.accuracy_colors = {
            ACCURACY_NONE: config.COLOR_TEXT,
            ACCURACY_GOOD: config.COLOR_HIT,
            ACCURACY_FAIR: config.COLOR_WRONG_KEY,
            ACCURACY_POOR: config.COLOR_MISS,
        }

        # The big card in the middle of the menu
        self.card_rect = pygame.Rect(0, 0, 760, 520)
        self.card_rect.center = (config.WINDOW_WIDTH // 2, 350)

        # The Start Game button. Game.py uses this rectangle to detect mouse clicks.
        self.start_button_rect = pygame.Rect(0, 0, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
        self.start_button_rect.center = (config.WINDOW_WIDTH // 2, 350)

        # The two buttons on the Game Over screen (Game uses them to detect clicks)
        self.play_again_button_rect = pygame.Rect(0, 0, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
        self.play_again_button_rect.center = (config.WINDOW_WIDTH // 2 - 150, 545)
        self.menu_button_rect = pygame.Rect(0, 0, config.BUTTON_WIDTH, config.BUTTON_HEIGHT)
        self.menu_button_rect.center = (config.WINDOW_WIDTH // 2 + 150, 545)

    # ------------------------------------------------------------
    # Small helper
    # ------------------------------------------------------------
    def _draw_text(self, text, font, color, **position):
        """Draw text. Give a position like center=(x, y), topleft=(x, y) or topright=(x, y)."""
        surface = font.render(text, True, color)
        rect = surface.get_rect(**position)
        self.screen.blit(surface, rect)
        return rect

    @staticmethod
    def _blend(color_a, color_b, amount):
        """Mix two colors. amount 0.0 gives color_a, 1.0 gives color_b."""
        return tuple(int(a + (b - a) * amount) for a, b in zip(color_a, color_b))

    def _draw_alpha_rect(self, rect, color, alpha, width=0, border_radius=0):
        """Draw a see-through rectangle. alpha: 0 = invisible, 255 = solid."""
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (*color, int(alpha)), surface.get_rect(),
                         width=width, border_radius=border_radius)
        self.screen.blit(surface, rect.topleft)

    def _draw_progress_bar(self, rect, fraction, color):
        """A rounded bar. fraction: 0.0 = empty, 1.0 = full."""
        fraction = max(0.0, min(1.0, fraction))
        pygame.draw.rect(self.screen, config.COLOR_BAR_TRACK, rect, border_radius=rect.height // 2)
        if fraction > 0:
            fill_rect = pygame.Rect(rect.left, rect.top, int(rect.width * fraction), rect.height)
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=rect.height // 2)

    def _accuracy_color(self, stats):
        return self.accuracy_colors[stats.get_accuracy_level()]

    @staticmethod
    def _event_color(event_text):
        """HIT is green, MISS is red, WRONG KEY is amber. Other text stays white."""
        if event_text.startswith("HIT"):
            return config.COLOR_HIT
        if event_text.startswith("MISS"):
            return config.COLOR_MISS
        if event_text.startswith("WRONG KEY"):
            return config.COLOR_WRONG_KEY
        return config.COLOR_TEXT

    @staticmethod
    def _format_key(key):
        """The text shown for the last wrong key. A space would look empty."""
        if key is None:
            return "-"
        if key == " ":
            return "Space"
        return key

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
    # GAME OVER screen
    # ------------------------------------------------------------
    def draw_game_over(self, stats, end_reason, remaining, mouse_pos):
        """stats = GameStats of the finished round, end_reason = END_TIME_UP or
        END_ALL_DONE, remaining = characters that were never typed or counted."""
        center_x = config.WINDOW_WIDTH // 2
        self.screen.fill(config.COLOR_BACKGROUND)

        # Card with a thin border (same style as the menu)
        pygame.draw.rect(self.screen, config.COLOR_PLAY_AREA, self.card_rect, border_radius=24)
        pygame.draw.rect(self.screen, config.COLOR_CARD_BORDER, self.card_rect, width=2, border_radius=24)

        # Title and the reason why the round ended
        self._draw_text("Game Over", self.font_title, config.COLOR_TEXT, center=(center_x, 165))
        if end_reason == END_ALL_DONE:
            reason_text = "You finished every character!"
        else:
            reason_text = "Time is up!"
        self._draw_text(reason_text, self.font_hud, config.COLOR_TEXT_DIM, center=(center_x, 220))

        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER,
                         (self.card_rect.left + 60, 255), (self.card_rect.right - 60, 255), 2)

        # Final statistics
        rows = [
            ("Hits", str(stats.hits), config.COLOR_TEXT),
            ("Misses", str(stats.misses), config.COLOR_TEXT),
            ("Key Presses", str(stats.key_presses), config.COLOR_TEXT),
            ("Wrong Keys", str(stats.wrong_keys), config.COLOR_TEXT),
            ("Accuracy", f"{stats.get_accuracy():.1f}%", self._accuracy_color(stats)),
            ("Left Over", str(remaining), config.COLOR_TEXT),
        ]
        left = self.card_rect.left + 190
        right = self.card_rect.right - 190
        y = 293
        for label, value, value_color in rows:
            self._draw_text(label, self.font_hud, config.COLOR_TEXT_DIM, midleft=(left, y))
            self._draw_text(value, self.font_hud_bold, value_color, midright=(right, y))
            y += 36

        # Buttons: Play Again (main action) and Main Menu (quieter)
        self._draw_button(self.play_again_button_rect, "Play Again", mouse_pos,
                          config.COLOR_ACCENT, config.COLOR_ACCENT_HOVER)
        self._draw_button(self.menu_button_rect, "Main Menu", mouse_pos,
                          config.COLOR_BUTTON_SECONDARY, config.COLOR_BUTTON_SECONDARY_HOVER)

        # Key hints below the card
        self._draw_text("ENTER  Play Again        M  Main Menu        ESC  Exit",
                        self.font_small, config.COLOR_TEXT_DIM, center=(center_x, 650))

    def _draw_button(self, rect, label, mouse_pos, color, hover_color):
        """Draw a rounded button. It uses the lighter color when the mouse is over it."""
        if rect.collidepoint(mouse_pos):
            button_color = hover_color
        else:
            button_color = color
        pygame.draw.rect(self.screen, button_color, rect, border_radius=config.BUTTON_RADIUS)
        self._draw_text(label, self.font_button, config.COLOR_TEXT, center=rect.center)

    # ------------------------------------------------------------
    # PLAYING screen
    # ------------------------------------------------------------
    def draw_playing(self, stats, characters, most_urgent, remaining, effects):
        """stats = GameStats, characters = the SORTED active list,
        most_urgent = the character to outline (or None), remaining = number to show,
        effects = the Effects object (flashes and the floating +1)."""
        self.screen.fill(config.COLOR_BACKGROUND)

        # Left: play area
        play_rect = pygame.Rect(0, 0, config.PLAY_AREA_WIDTH, config.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PLAY_AREA, play_rect)

        # Subtle green flash after a hit
        hit_flash = effects.get_hit_flash()
        if hit_flash > 0:
            self._draw_alpha_rect(play_rect, config.COLOR_HIT, 40 * hit_flash)

        self._draw_dead_bar(effects.get_dead_bar_flash())

        # Falling characters (drawn on top of the Dead Bar)
        self._draw_characters(characters, most_urgent)
        self._draw_floating_texts(effects.floating_texts)

        # Amber border flash after a wrong key
        wrong_flash = effects.get_wrong_flash()
        if wrong_flash > 0:
            self._draw_alpha_rect(play_rect, config.COLOR_WRONG_KEY, 230 * wrong_flash, width=6)

        self._draw_stats_panel(stats, remaining, effects)

    def _draw_dead_bar(self, flash):
        """The Dead Bar. flash (0.0 to 1.0) is the strength of the red highlight after a miss."""
        bar_rect = pygame.Rect(0, config.DEAD_BAR_Y, config.PLAY_AREA_WIDTH, config.DEAD_BAR_HEIGHT)
        bar_color = config.COLOR_DEAD_BAR
        if flash > 0:
            glow_rect = pygame.Rect(0, config.DEAD_BAR_Y - 40, config.PLAY_AREA_WIDTH,
                                    40 + config.DEAD_BAR_HEIGHT)
            self._draw_alpha_rect(glow_rect, config.COLOR_DEAD_BAR, 110 * flash)
            bar_color = self._blend(config.COLOR_DEAD_BAR, config.COLOR_DEAD_BAR_FLASH, flash)
            bar_rect.inflate_ip(0, int(8 * flash))
        pygame.draw.rect(self.screen, bar_color, bar_rect)
        self._draw_text("DEAD BAR", self.font_small, bar_color,
                        topleft=(20, config.DEAD_BAR_Y + 14))

    def _draw_characters(self, characters, most_urgent):
        """Draw every falling character. A character's y is the line where the
        letter 'stands' (its baseline), so it touches the Dead Bar exactly when
        Character.has_crossed() says it crossed."""
        baseline_shift = -self.font_character.get_descent()   # space below the baseline

        for character in characters:
            color = self.category_colors[character.get_category()]
            surface = self.font_character.render(character.symbol, True, color)
            rect = surface.get_rect(midbottom=(int(character.x), int(character.y) + baseline_shift))

            # Do not draw characters that are completely outside the window
            if rect.bottom < 0 or rect.top > config.WINDOW_HEIGHT:
                continue
            self.screen.blit(surface, rect)

            # A thin outline marks the most urgent character (closest to the Dead Bar).
            # Purple = normal, orange = getting close, red = very close.
            if character is most_urgent:
                outline_color = self.urgency_colors.get(character.get_urgency_level(),
                                                        config.COLOR_URGENCY_NORMAL)
                pygame.draw.rect(self.screen, outline_color, rect.inflate(18, 4),
                                 width=2, border_radius=10)

    def _draw_floating_texts(self, floating_texts):
        """Draw the green +1 at the place of the typed character. It rises and fades out."""
        for floating in floating_texts:
            progress = floating.get_progress()
            surface = self.font_hud_bold.render(floating.text, True, config.COLOR_HIT)
            surface.set_alpha(int(255 * (1 - progress)))
            # floating.y is the baseline of the character; start in the middle of the letter
            y = max(20, floating.y - 25 - config.EFFECT_FLOAT_RISE_PIXELS * progress)
            self.screen.blit(surface, surface.get_rect(center=(int(floating.x), int(y))))

    def _draw_stats_panel(self, stats, remaining, effects):
        panel_x = config.PLAY_AREA_WIDTH
        panel_rect = pygame.Rect(panel_x, 0, config.PANEL_WIDTH, config.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, config.COLOR_PANEL, panel_rect)
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER,
                         (panel_x, 0), (panel_x, config.WINDOW_HEIGHT), 2)

        left = panel_x + 24
        right = panel_x + config.PANEL_WIDTH - 24
        bar_width = right - left

        self._draw_text("STATS", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 24))

        # Time Left: big number and a bar that shrinks. Both turn red in the last seconds.
        if stats.is_time_low():
            time_color = config.COLOR_MISS
        else:
            time_color = config.COLOR_TEXT
        self._draw_text("TIME LEFT", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 54))
        self._draw_text(self._format_time(stats.time_left), self.font_timer, time_color,
                        topleft=(left, 74))
        if stats.is_time_low():
            bar_color = config.COLOR_MISS
        else:
            bar_color = config.COLOR_ACCENT
        self._draw_progress_bar(pygame.Rect(left, 150, bar_width, 10),
                                stats.get_time_fraction(), bar_color)

        # Numbers. Hits and Misses get a short highlight, Accuracy has its own color.
        rows = [
            ("Hits", str(stats.hits), config.COLOR_TEXT,
             config.COLOR_HIT, effects.get_hits_highlight()),
            ("Misses", str(stats.misses), config.COLOR_TEXT,
             config.COLOR_MISS, effects.get_misses_highlight()),
            ("Key Presses", str(stats.key_presses), config.COLOR_TEXT, None, 0),
            ("Accuracy", f"{stats.get_accuracy():.1f}%", self._accuracy_color(stats), None, 0),
            ("Remaining", str(remaining), config.COLOR_TEXT, None, 0),
        ]
        y = 192
        for label, value, value_color, highlight_color, strength in rows:
            if strength > 0:
                row_rect = pygame.Rect(left - 8, y - 16, bar_width + 16, 32)
                self._draw_alpha_rect(row_rect, highlight_color, 70 * strength, border_radius=8)
                value_color = self._blend(value_color, highlight_color, strength)
            self._draw_text(label, self.font_hud, config.COLOR_TEXT_DIM, midleft=(left, y))
            self._draw_text(value, self.font_hud_bold, value_color, midright=(right, y))
            y += 34

        # The last wrong key (it stays until the round ends)
        last_key = effects.last_wrong_key
        if last_key is None:
            key_color = config.COLOR_TEXT_DIM
        else:
            key_color = config.COLOR_WRONG_KEY
        self._draw_text("Last Wrong Key", self.font_hud, config.COLOR_TEXT_DIM, midleft=(left, y))
        self._draw_text(self._format_key(last_key), self.font_hud_bold, key_color,
                        midright=(right, y))

        # Characters completed (hit or missed) out of all characters of the round
        completed = stats.hits + stats.misses
        self._draw_text("COMPLETED", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 392))
        self._draw_text(f"{completed} / {config.TOTAL_CHARACTERS}", self.font_small,
                        config.COLOR_TEXT, topright=(right, 392))
        self._draw_progress_bar(pygame.Rect(left, 420, bar_width, 10),
                                completed / config.TOTAL_CHARACTERS, config.COLOR_LOWERCASE)

        # Recent events (read from our Stack through GameStats). The newest is the
        # brightest; older events fade towards the panel color.
        pygame.draw.line(self.screen, config.COLOR_CARD_BORDER, (left, 450), (right, 450), 2)
        self._draw_text("RECENT EVENTS", self.font_small, config.COLOR_TEXT_DIM, topleft=(left, 462))
        events = stats.get_recent_events(5)
        if len(events) == 0:
            self._draw_text("No events yet", self.font_small, config.COLOR_TEXT_DIM,
                            topleft=(left, 494))
        else:
            event_y = 494
            for index, event_text in enumerate(events):
                color = self._blend(self._event_color(event_text), config.COLOR_PANEL, index * 0.1)
                self._draw_text(event_text, self.font_small, color, topleft=(left, event_y))
                event_y += 26

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