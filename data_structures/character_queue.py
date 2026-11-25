class Node:
    """One box in the chain. It holds one item and a link to the next box."""

    def __init__(self, data):
        self.data = data    # the item we store (for example "k")
        self.next = None    # link to the next Node (None = no next box)


class CharacterQueue:
    def __init__(self):
        self.front = None   # the Node that will leave first
        self.rear = None    # the Node that joined last
        self._size = 0      # how many items are inside

    def enqueue(self, item):
        """Add an item at the REAR (back of the line)."""
        new_node = Node(item)
        if self.rear is None:
            # Queue was empty: the new node is both front and rear
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node   # old last node points to the new node
            self.rear = new_node        # the new node becomes the last one
        self._size += 1

    def dequeue(self):
        
        if self.front is None:
            return None                 # safe: nothing to remove
        removed_node = self.front
        self.front = removed_node.next  # second node becomes the front
        if self.front is None:
            self.rear = None            # queue became empty, so rear is empty too
        self._size -= 1
        return removed_node.data

    def peek(self):
        """Look at the front item WITHOUT removing it. Returns None if empty."""
        if self.front is None:
            return None
        return self.front.data

    def is_empty(self):
        """True if there are no items."""
        return self.front is None

    def size(self):
        """Return how many items are in the queue."""
        return self._size

    def to_list(self):
        """Return all items as a normal list, front first. Does NOT change the queue.
        Used for tests and debugging."""
        items = []
        current = self.front
        while current is not None:
            items.append(current.data)
            current = current.next
        return items