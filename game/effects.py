"""
effects.py
Short visual effects for the playing screen: the floating +1, the green and
amber flashes, and the highlights of the Dead Bar and the statistics.

Every effect is a timer in seconds. A trigger_...() method starts it, update(dt)
makes it smaller every frame, and a get_...() method tells the Renderer how
strong it is right now: 1.0 = just started, 0.0 = finished.

Effects are only for the eyes. They never change hits, misses or any game rule.
This file has NO Pygame code, so it is easy to test.
"""

import config


class FloatingText:
    """One floating '+1'. It stays where the character was typed and fades out."""

    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y          # where the character stood
        self.age = 0.0      # seconds since it appeared

    def get_progress(self):
        """0.0 when it appears, 1.0 when it has finished."""
        return min(self.age / config.EFFECT_FLOAT_SECONDS, 1.0)

    def is_finished(self):
        return self.age >= config.EFFECT_FLOAT_SECONDS


class Effects:
    def __init__(self):
        self.clear()

    def clear(self):
        """Stop every effect. Used when a new round starts or on the Main Menu."""
        self.hit_flash = 0.0            # green flash of the play area
        self.hits_highlight = 0.0       # green Hits statistic
        self.wrong_flash = 0.0          # amber border of the play area
        self.dead_bar_flash = 0.0       # red Dead Bar
        self.misses_highlight = 0.0     # red Misses statistic
        self.last_wrong_key = None      # the last wrong key of this round
        self.floating_texts = []        # list of FloatingText

    # ---- start an effect ----
    def trigger_hit(self, x, y):
        """A correct key. (x, y) is the position of the typed character."""
        self.hit_flash = config.EFFECT_HIT_FLASH_SECONDS
        self.hits_highlight = config.EFFECT_STAT_HIGHLIGHT_SECONDS
        self.floating_texts.append(FloatingText("+1", x, y))

    def trigger_wrong_key(self, key):
        self.wrong_flash = config.EFFECT_WRONG_FLASH_SECONDS
        self.last_wrong_key = key

    def trigger_miss(self):
        self.dead_bar_flash = config.EFFECT_DEAD_BAR_FLASH_SECONDS
        self.misses_highlight = config.EFFECT_STAT_HIGHLIGHT_SECONDS

    # ---- one frame ----
    def update(self, dt):
        """Make every timer smaller. dt = seconds since the last frame."""
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.hits_highlight = max(0.0, self.hits_highlight - dt)
        self.wrong_flash = max(0.0, self.wrong_flash - dt)
        self.dead_bar_flash = max(0.0, self.dead_bar_flash - dt)
        self.misses_highlight = max(0.0, self.misses_highlight - dt)

        for text in self.floating_texts:
            text.age += dt
        # keep only the floating texts that are still visible
        self.floating_texts = [text for text in self.floating_texts if not text.is_finished()]

    # ---- strength: 1.0 = just started, 0.0 = finished ----
    def get_hit_flash(self):
        return self.hit_flash / config.EFFECT_HIT_FLASH_SECONDS

    def get_hits_highlight(self):
        return self.hits_highlight / config.EFFECT_STAT_HIGHLIGHT_SECONDS

    def get_wrong_flash(self):
        return self.wrong_flash / config.EFFECT_WRONG_FLASH_SECONDS

    def get_dead_bar_flash(self):
        return self.dead_bar_flash / config.EFFECT_DEAD_BAR_FLASH_SECONDS

    def get_misses_highlight(self):
        return self.misses_highlight / config.EFFECT_STAT_HIGHLIGHT_SECONDS