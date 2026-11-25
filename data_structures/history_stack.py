"""
history_stack.py
A Stack built by ourselves using a Linked List.
Rule of a Stack: LIFO = Last In, First Out.
In the game it stores events such as HIT, MISS and WRONG KEY.
"""

from data_structures.character_queue import Node   # we reuse the same "box"


class HistoryStack:
    def __init__(self):
        self.top = None     # the Node on top (the newest item)
        self._size = 0

    def push(self, item):
        """Put an item on TOP of the stack."""
        new_node = Node(item)
        new_node.next = self.top    # new node points to the old top
        self.top = new_node         # new node becomes the top
        self._size += 1

    def pop(self):
        """Remove and return the TOP item. Returns None if empty."""
        if self.top is None:
            return None
        removed_node = self.top
        self.top = removed_node.next    # the node below becomes the top
        self._size -= 1
        return removed_node.data

    def peek(self):
        """Look at the TOP item without removing it. Returns None if empty."""
        if self.top is None:
            return None
        return self.top.data

    def is_empty(self):
        """True if there are no items."""
        return self.top is None

    def size(self):
        """Return how many items are in the stack."""
        return self._size

    def to_list(self):
        """Return all items as a normal list, NEWEST FIRST.
        It only reads the stack. Nothing is removed or changed.
        The Recent Events panel will use the first few items of this list."""
        items = []
        current = self.top
        while current is not None:
            items.append(current.data)
            current = current.next
        return items