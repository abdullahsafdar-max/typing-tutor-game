"""
test_data_structures.py
Tests for our own data structures.
Milestone 2: Queue tests. (Stack, Searching, Sorting tests come later.)
"""

import unittest

from data_structures.character_queue import CharacterQueue
from game.character import Character


class TestCharacterQueue(unittest.TestCase):
    def setUp(self):
        """Runs before EVERY test, so each test gets a fresh empty queue."""
        self.queue = CharacterQueue()

    def test_new_queue_is_empty(self):
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 0)

    def test_enqueue_one_item(self):
        self.queue.enqueue("a")
        self.assertFalse(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 1)
        self.assertEqual(self.queue.peek(), "a")

    def test_enqueue_updates_size(self):
        for symbol in "abc":
            self.queue.enqueue(symbol)
        self.assertEqual(self.queue.size(), 3)

    def test_fifo_order(self):
        for symbol in "abc":
            self.queue.enqueue(symbol)
        self.assertEqual(self.queue.dequeue(), "a")
        self.assertEqual(self.queue.dequeue(), "b")
        self.assertEqual(self.queue.dequeue(), "c")

    def test_dequeue_reduces_size(self):
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.queue.dequeue()
        self.assertEqual(self.queue.size(), 1)

    def test_peek_does_not_remove(self):
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.assertEqual(self.queue.peek(), "a")
        self.assertEqual(self.queue.peek(), "a")
        self.assertEqual(self.queue.size(), 2)

    def test_dequeue_on_empty_returns_none(self):
        self.assertIsNone(self.queue.dequeue())
        self.assertEqual(self.queue.size(), 0)   # size must not become -1

    def test_peek_on_empty_returns_none(self):
        self.assertIsNone(self.queue.peek())

    def test_front_and_rear_after_last_item_removed(self):
        self.queue.enqueue("a")
        self.queue.dequeue()
        self.assertIsNone(self.queue.front)
        self.assertIsNone(self.queue.rear)
        self.assertTrue(self.queue.is_empty())

    def test_queue_works_again_after_becoming_empty(self):
        self.queue.enqueue("a")
        self.queue.dequeue()
        self.queue.enqueue("x")
        self.queue.enqueue("y")
        self.assertEqual(self.queue.size(), 2)
        self.assertEqual(self.queue.dequeue(), "x")
        self.assertEqual(self.queue.dequeue(), "y")
        self.assertTrue(self.queue.is_empty())

    def test_to_list_keeps_queue_unchanged(self):
        for symbol in "abc":
            self.queue.enqueue(symbol)
        self.assertEqual(self.queue.to_list(), ["a", "b", "c"])
        self.assertEqual(self.queue.size(), 3)   # nothing was removed

    def test_queue_can_hold_character_objects(self):
        char = Character("k", 200)
        self.queue.enqueue(char)
        self.assertIs(self.queue.dequeue(), char)   # same object comes out

    def test_queue_with_80_items(self):
        for number in range(80):
            self.queue.enqueue(number)
        self.assertEqual(self.queue.size(), 80)
        for number in range(80):
            self.assertEqual(self.queue.dequeue(), number)
        self.assertTrue(self.queue.is_empty())


if __name__ == "__main__":
    unittest.main()