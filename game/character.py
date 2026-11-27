"""
character.py
One falling character (a letter or a digit).
This file has NO Pygame code. It only stores data and does simple math.
"""

from config import (CHARACTER_FALL_SPEED, DEAD_BAR_Y, SPAWN_Y,
                    URGENCY_DANGER_DISTANCE, URGENCY_WARNING_DISTANCE)

# The three urgency levels (the renderer picks the outline color from them)
URGENCY_NORMAL = "normal"
URGENCY_WARNING = "warning"
URGENCY_DANGER = "danger"


class Character:
    def __init__(self, symbol, x, y=SPAWN_Y, speed=CHARACTER_FALL_SPEED):
        self.symbol = symbol    # the text, for example "k", "R" or "7"
        self.x = x              # horizontal position (never changes)
        self.y = float(y)       # vertical position (grows as it falls)
        self.speed = speed      # pixels per second

    def move(self, dt):
        """Move down. dt = seconds passed since the last frame."""
        self.y += self.speed * dt

    def has_crossed(self, dead_bar_y=DEAD_BAR_Y):
        """True when the character has reached or passed the Dead Bar."""
        return self.y >= dead_bar_y

    def get_urgency_level(self, dead_bar_y=DEAD_BAR_Y):
        """How close is the character to the Dead Bar?
        Returns 'danger' (very close), 'warning' (getting close) or 'normal'.
        It only reads y. It never moves the character."""
        distance = dead_bar_y - self.y
        if distance <= URGENCY_DANGER_DISTANCE:
            return URGENCY_DANGER
        if distance <= URGENCY_WARNING_DISTANCE:
            return URGENCY_WARNING
        return URGENCY_NORMAL

    def get_category(self):
        """Return 'digit', 'upper' or 'lower'. The renderer uses this for color."""
        if self.symbol.isdigit():
            return "digit"
        if self.symbol.isupper():
            return "upper"
        return "lower"

    def __repr__(self):
        """How the object looks when printed. Helpful for tests and debugging."""
        return f"Character('{self.symbol}', x={self.x}, y={self.y:.1f})"