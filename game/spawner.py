"""
spawner.py
Creates the random characters and controls when they start falling.

It uses three of our five data structures:
  - Queue : the upcoming symbols wait here (first in, first out)
  - List  : the characters that are falling right now
  - Sort  : after every move, the list is sorted (greatest y first)

This file has NO Pygame code, so it is easy to test.
"""

import random

import config
from data_structures.character_queue import CharacterQueue
from data_structures.sorting import sort_by_height
from game.character import Character


class Spawner:
    def __init__(self, total=config.TOTAL_CHARACTERS, interval=config.SPAWN_INTERVAL_SECONDS):
        self.interval = interval            # seconds between two spawns
        self.queue = CharacterQueue()       # upcoming symbols, for example "k", "R", "7"
        self.active_characters = []         # Character objects that are falling now
        self.spawn_timer = 0.0              # time collected since the last spawn

        self._fill_queue(total)

    def _fill_queue(self, total):
        """Pick `total` random symbols and put them in the Queue."""
        for _ in range(total):
            symbol = random.choice(config.CHARACTER_POOL)   # a-z, A-Z or 0-9
            self.queue.enqueue(symbol)

    def update(self, dt):
        """Do one frame of work. dt = seconds since the last frame.
        The order of the 3 steps is important."""

        # Step 1: move every falling character down
        for character in self.active_characters:
            character.move(dt)

        # Step 2: spawn new characters when enough time has passed
        self.spawn_timer += dt
        while self.spawn_timer >= self.interval and not self.queue.is_empty():
            self._spawn_one()
            self.spawn_timer -= self.interval

        # Step 3: sort the list so the lowest character (greatest y) is first
        sort_by_height(self.active_characters)

    def _spawn_one(self):
        """Take the front symbol out of the Queue and start it falling."""
        symbol = self.queue.dequeue()
        x = random.randint(config.SPAWN_X_MIN, config.SPAWN_X_MAX)
        character = Character(symbol, x, config.SPAWN_Y)
        self.active_characters.append(character)

    def get_most_urgent(self):
        """Return the lowest character that has NOT crossed the Dead Bar yet.
        Returns None if there is no such character.

        This works because the list is sorted: the characters closest to the
        Dead Bar are at the front. We walk from the front and stop at the
        first character that has not crossed, so we never look at the rest."""
        for character in self.active_characters:
            if not character.has_crossed():
                return character
        return None

    def queue_size(self):
        """How many symbols are still waiting in the Queue."""
        return self.queue.size()

    def active_count(self):
        """How many characters are falling right now."""
        return len(self.active_characters)