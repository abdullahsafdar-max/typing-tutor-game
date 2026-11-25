"""
searching.py
Linear Search, written by ourselves.
In the game it finds the falling character that matches the pressed key.
"""


def find_matching_character(characters, key):
    """Check EVERY character in the list, one by one.
    Among the characters whose symbol equals `key`, return the one with the
    greatest y (the one closest to the Dead Bar).
    Return None if no character matches.
    The comparison is case-sensitive: "a" does not match "A".
    This works correctly even if the list is not sorted."""
    best_match = None
    for character in characters:
        if character.symbol == key:
            if best_match is None or character.y > best_match.y:
                best_match = character
    return best_match