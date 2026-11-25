"""
sorting.py
Insertion Sort, written by ourselves (we do NOT use sorted() or list.sort()).
In the game it sorts the falling characters by their vertical position.
"""


def sort_by_height(characters):
    """Sort the list IN PLACE by y, from the greatest y to the smallest y.
    On the screen a bigger y means lower, so the character closest to the
    Dead Bar comes first.
    The sort is stable: characters with the same y keep their original order."""
    for i in range(1, len(characters)):
        current = characters[i]         # the item we want to place correctly
        j = i - 1
        # Shift items that should come AFTER `current` one place to the right.
        # We use "<" (not "<="), so items with an equal y are NOT moved past
        # each other. This is what makes the sort stable.
        while j >= 0 and characters[j].y < current.y:
            characters[j + 1] = characters[j]
            j -= 1
        characters[j + 1] = current     # drop the item into its place
    return characters