"""
typing_handler.py
Decides what happens when the player types a key.

It connects three things we already built:
  - Spawner            : owns the list of falling characters
  - find_matching_character : our Linear Search
  - GameStats          : counts hits and key presses, and pushes events on the Stack

This file has NO Pygame code, so it is easy to test.
"""

from data_structures.searching import find_matching_character

# The three possible results of handle_key()
RESULT_HIT = "hit"
RESULT_WRONG_KEY = "wrong_key"
RESULT_IGNORED = "ignored"


class TypingHandler:
    def __init__(self, spawner, stats):
        self.spawner = spawner
        self.stats = stats
        self.last_hit_character = None   # the Character removed by the last hit

    @staticmethod
    def is_typed_character(symbol):
        """True only for ONE printable character, like "a", "7", "!" or " ".

        Keys like Shift and Ctrl give an empty string "".
        Enter gives "\\r", Escape gives "\\x1b", Tab gives "\\t".
        None of those are printable, so they are not typed characters.

        Why len(symbol) == 1? Because "".isprintable() is True in Python,
        so the empty string would wrongly pass without this check."""
        return len(symbol) == 1 and symbol.isprintable()

    def handle_key(self, symbol):
        """Process one typed key. `symbol` is the text of the key (event.unicode).
        Returns RESULT_HIT, RESULT_WRONG_KEY or RESULT_IGNORED.

        last_hit_character is cleared at the start of every call, so it is
        not None only right after a hit. The Game uses it to show the +1
        at the position of the character that was just typed."""
        self.last_hit_character = None

        # 1. Ignore keys that are not typed characters (Shift, Ctrl, Enter, Escape...)
        if not self.is_typed_character(symbol):
            return RESULT_IGNORED

        # 2. Search only the characters that have not crossed the Dead Bar.
        #    The search is case-sensitive and returns the one with the greatest y.
        typable_characters = self.spawner.get_typable_characters()
        match = find_matching_character(typable_characters, symbol)

        # 3a. No match: wrong key. Key Presses +1, Misses are NOT changed.
        if match is None:
            self.stats.record_wrong_key(symbol)
            return RESULT_WRONG_KEY

        # 3b. Match: remove that exact character, then count the hit.
        self.spawner.remove_character(match)
        self.stats.record_hit(match.symbol)
        self.last_hit_character = match
        return RESULT_HIT