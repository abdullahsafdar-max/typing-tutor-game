from config import (ACCURACY_FAIR_MIN, ACCURACY_GOOD_MIN, GAME_DURATION_SECONDS,
                    TIME_WARNING_SECONDS)
from data_structures.history_stack import HistoryStack

# The four accuracy levels (the renderer picks the color from them)
ACCURACY_NONE = "none"      # no key has been pressed yet
ACCURACY_GOOD = "good"
ACCURACY_FAIR = "fair"
ACCURACY_POOR = "poor"


class GameStats:
    def __init__(self, duration=GAME_DURATION_SECONDS):
        self.hits = 0
        self.misses = 0
        self.key_presses = 0
        self.wrong_keys = 0
        self.duration = float(duration)
        self.time_left = float(duration)
        self.events = HistoryStack()

    def record_hit(self, symbol):
        self.hits += 1
        self.key_presses += 1
        self.events.push(f"HIT '{symbol}'")

    def record_miss(self, symbol):
        self.misses += 1
        self.events.push(f"MISS '{symbol}'")

    def record_wrong_key(self, key):
        self.key_presses += 1
        self.wrong_keys += 1
        self.events.push(f"WRONG KEY '{key}'")

    def get_accuracy(self):
        if self.key_presses == 0:
            return 0.0
        return self.hits / self.key_presses * 100

    def get_accuracy_level(self):
        """Return ACCURACY_NONE, ACCURACY_GOOD, ACCURACY_FAIR or ACCURACY_POOR."""
        if self.key_presses == 0:
            return ACCURACY_NONE
        accuracy = self.get_accuracy()
        if accuracy >= ACCURACY_GOOD_MIN:
            return ACCURACY_GOOD
        if accuracy >= ACCURACY_FAIR_MIN:
            return ACCURACY_FAIR
        return ACCURACY_POOR

    def get_remaining(self, queue_size, active_count):
        return queue_size + active_count

    def update_timer(self, dt):
        self.time_left -= dt
        if self.time_left < 0:
            self.time_left = 0.0

    def is_time_up(self):
        return self.time_left <= 0

    def get_time_fraction(self):
        """Time left as a number from 0.0 (no time) to 1.0 (full time)."""
        if self.duration <= 0:
            return 0.0
        return self.time_left / self.duration

    def is_time_low(self):
        """True in the last seconds of the round (the timer turns red)."""
        return self.time_left <= TIME_WARNING_SECONDS

    def get_recent_events(self, count=5):
        return self.events.to_list()[:count]