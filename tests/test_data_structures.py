"""
test_data_structures.py
Tests for our own data structures:
Queue (Milestone 2), Stack, Searching and Sorting (Milestone 3).
"""

import unittest

from data_structures.character_queue import CharacterQueue
from data_structures.history_stack import HistoryStack
from data_structures.searching import find_matching_character
from data_structures.sorting import sort_by_height
from game.character import Character


# ===============================================================
# QUEUE
# ===============================================================
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


# ===============================================================
# STACK
# ===============================================================
class TestHistoryStack(unittest.TestCase):
    def setUp(self):
        self.stack = HistoryStack()

    def test_new_stack_is_empty(self):
        self.assertTrue(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 0)

    def test_push_one_item(self):
        self.stack.push("HIT 'a'")
        self.assertFalse(self.stack.is_empty())
        self.assertEqual(self.stack.size(), 1)
        self.assertEqual(self.stack.peek(), "HIT 'a'")

    def test_push_updates_size(self):
        for event in ["e1", "e2", "e3"]:
            self.stack.push(event)
        self.assertEqual(self.stack.size(), 3)

    def test_lifo_order(self):
        for event in ["e1", "e2", "e3"]:
            self.stack.push(event)
        self.assertEqual(self.stack.pop(), "e3")   # last in, first out
        self.assertEqual(self.stack.pop(), "e2")
        self.assertEqual(self.stack.pop(), "e1")

    def test_pop_reduces_size(self):
        self.stack.push("e1")
        self.stack.push("e2")
        self.stack.pop()
        self.assertEqual(self.stack.size(), 1)

    def test_peek_does_not_remove(self):
        self.stack.push("e1")
        self.stack.push("e2")
        self.assertEqual(self.stack.peek(), "e2")
        self.assertEqual(self.stack.peek(), "e2")
        self.assertEqual(self.stack.size(), 2)

    def test_pop_on_empty_returns_none(self):
        self.assertIsNone(self.stack.pop())
        self.assertEqual(self.stack.size(), 0)   # size must not become -1

    def test_peek_on_empty_returns_none(self):
        self.assertIsNone(self.stack.peek())

    def test_to_list_returns_newest_first(self):
        for event in ["e1", "e2", "e3"]:
            self.stack.push(event)
        self.assertEqual(self.stack.to_list(), ["e3", "e2", "e1"])

    def test_to_list_on_empty_stack(self):
        self.assertEqual(self.stack.to_list(), [])

    def test_to_list_does_not_modify_stack(self):
        for event in ["e1", "e2", "e3"]:
            self.stack.push(event)
        self.stack.to_list()
        self.assertEqual(self.stack.size(), 3)
        self.assertEqual(self.stack.peek(), "e3")
        self.assertEqual(self.stack.to_list(), ["e3", "e2", "e1"])  # same again

    def test_to_list_after_pop(self):
        for event in ["e1", "e2", "e3"]:
            self.stack.push(event)
        self.stack.pop()
        self.assertEqual(self.stack.to_list(), ["e2", "e1"])

    def test_stack_works_again_after_becoming_empty(self):
        self.stack.push("e1")
        self.stack.pop()
        self.assertIsNone(self.stack.top)
        self.stack.push("e2")
        self.assertEqual(self.stack.peek(), "e2")
        self.assertEqual(self.stack.size(), 1)

    def test_stack_can_store_game_event_text(self):
        self.stack.push("HIT 'k'")
        self.stack.push("MISS 'R'")
        self.stack.push("WRONG KEY 'x'")
        self.assertEqual(
            self.stack.to_list(),
            ["WRONG KEY 'x'", "MISS 'R'", "HIT 'k'"],
        )


# ===============================================================
# SORTING
# ===============================================================
def make_characters(*y_values):
    """Helper: make Character objects with the given y positions.
    Symbols are a, b, c, ... so we can tell them apart."""
    return [Character(chr(ord("a") + i), 0, y) for i, y in enumerate(y_values)]


class TestSorting(unittest.TestCase):
    def test_greatest_y_comes_first(self):
        chars = make_characters(50, 300, 120)
        sort_by_height(chars)
        self.assertEqual([c.y for c in chars], [300, 120, 50])

    def test_empty_list(self):
        chars = []
        sort_by_height(chars)
        self.assertEqual(chars, [])

    def test_single_item(self):
        chars = make_characters(100)
        sort_by_height(chars)
        self.assertEqual([c.y for c in chars], [100])

    def test_already_sorted_list_stays_same(self):
        chars = make_characters(300, 200, 100)
        sort_by_height(chars)
        self.assertEqual([c.y for c in chars], [300, 200, 100])

    def test_reverse_order_list(self):
        chars = make_characters(10, 20, 30, 40)
        sort_by_height(chars)
        self.assertEqual([c.y for c in chars], [40, 30, 20, 10])

    def test_equal_heights_keep_original_order(self):
        chars = make_characters(100, 100, 100)    # symbols a, b, c
        sort_by_height(chars)
        self.assertEqual([c.symbol for c in chars], ["a", "b", "c"])

    def test_stable_with_mixed_equal_heights(self):
        # a=100, b=200, c=100, d=200
        chars = make_characters(100, 200, 100, 200)
        sort_by_height(chars)
        # b and d (y=200) keep their order, a and c (y=100) keep their order
        self.assertEqual([c.symbol for c in chars], ["b", "d", "a", "c"])

    def test_sorts_in_place_and_returns_same_list(self):
        chars = make_characters(10, 20)
        result = sort_by_height(chars)
        self.assertIs(result, chars)
        self.assertEqual([c.y for c in chars], [20, 10])


# ===============================================================
# SEARCHING
# ===============================================================
class TestSearching(unittest.TestCase):
    def test_finds_matching_character(self):
        chars = [Character("a", 0, 300), Character("b", 0, 200), Character("c", 0, 100)]
        found = find_matching_character(chars, "b")
        self.assertIs(found, chars[1])             # the exact same object

    def test_returns_none_when_not_found(self):
        chars = [Character("a", 0, 300), Character("b", 0, 200)]
        self.assertIsNone(find_matching_character(chars, "z"))

    def test_empty_list_returns_none(self):
        self.assertIsNone(find_matching_character([], "a"))

    def test_search_is_case_sensitive(self):
        chars = [Character("A", 0, 300)]
        self.assertIsNone(find_matching_character(chars, "a"))
        self.assertIs(find_matching_character(chars, "A"), chars[0])

    def test_digit_can_be_found(self):
        chars = [Character("7", 0, 300), Character("k", 0, 200)]
        self.assertIs(find_matching_character(chars, "7"), chars[0])

    def test_duplicates_return_greatest_y_even_if_list_not_sorted(self):
        # The HIGH one (y=100) is first in the list, the LOW one (y=400) is last
        chars = [Character("a", 0, 100), Character("b", 0, 250), Character("a", 0, 400)]
        found = find_matching_character(chars, "a")
        self.assertIs(found, chars[2])
        self.assertEqual(found.y, 400)

    def test_three_duplicates_return_the_one_with_greatest_y(self):
        chars = [Character("a", 0, 100), Character("a", 0, 500), Character("a", 0, 300)]
        found = find_matching_character(chars, "a")
        self.assertEqual(found.y, 500)

    def test_duplicates_after_sorting(self):
        chars = [Character("a", 0, 100), Character("b", 0, 250), Character("a", 0, 400)]
        sort_by_height(chars)
        found = find_matching_character(chars, "a")
        self.assertEqual(found.y, 400)

    def test_duplicates_with_same_y_return_first_one(self):
        chars = [Character("a", 0, 200), Character("a", 0, 200)]
        found = find_matching_character(chars, "a")
        self.assertIs(found, chars[0])

    def test_search_does_not_change_the_list(self):
        chars = [Character("a", 0, 300), Character("b", 0, 200)]
        find_matching_character(chars, "b")
        self.assertEqual(len(chars), 2)
        self.assertEqual([c.symbol for c in chars], ["a", "b"])


if __name__ == "__main__":
    unittest.main()