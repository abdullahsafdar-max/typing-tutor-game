"""
round_manager.py
The rules of ONE round of the game: the timer, the misses and the end of the game.

Game calls update() once per frame while the game is playing, and then asks
is_over() to know if the Game Over screen must be shown.

It connects two things we already built:
  - Spawner   : owns the Queue and the list of falling characters
  - GameStats : counts hits and misses, runs the timer, owns the event Stack

This file has NO Pygame code, so it is easy to test.
"""

# The two possible reasons for the end of a round
END_TIME_UP = "time_up"          # the 60 seconds are finished
END_ALL_DONE = "all_done"        # no character is left in the Queue or on the screen


class RoundManager:
    def __init__(self, spawner, stats):
        self.spawner = spawner
        self.stats = stats

    def update(self, dt):
        """Do one frame of work. dt = seconds since the last frame.
        The order of the steps is important."""

        # Step 1: the timer goes down (it never goes below zero)
        self.stats.update_timer(dt)

        # Step 2: move, spawn and sort the characters
        self.spawner.update(dt)

        # Step 3: every character that crossed the Dead Bar is one MISS.
        # remove_crossed_characters() takes them out of the list, so each
        # character is counted exactly once.
        for character in self.spawner.remove_crossed_characters():
            self.stats.record_miss(character.symbol)

    def is_over(self):
        """True when the round must end."""
        return self.end_reason() is not None

    def end_reason(self):
        """Return END_ALL_DONE, END_TIME_UP, or None if the round continues.
        If both happen in the same frame, END_ALL_DONE wins, because the
        player finished every character."""
        if self.spawner.queue_size() == 0 and self.spawner.active_count() == 0:
            return END_ALL_DONE
        if self.stats.is_time_up():
            return END_TIME_UP
        return None