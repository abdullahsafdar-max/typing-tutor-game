from config import GAME_DURATION_SECONDS
from data_structures.history_stack import HistoryStack


class GameStats:
    def __init__(self, duration=GAME_DURATION_SECONDS):
        self.hits = 0
        self.misses = 0
        self.key_presses = 0
        self.wrong_keys = 0
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

    def get_remaining(self, queue_size, active_count):
        return queue_size + active_count

    def update_timer(self, dt):
        self.time_left -= dt
        if self.time_left < 0:
            self.time_left = 0.0

    def is_time_up(self):
        return self.time_left <= 0

    def get_recent_events(self, count=5):
        return self.events.to_list()[:count]