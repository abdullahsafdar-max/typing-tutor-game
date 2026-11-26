"""
test_spawner.py
Tests for the Spawner class (Milestone 6). No Pygame window is needed.

Many tests use  Spawner(total=5, interval=1.0)  because whole numbers
make the maths easy to follow.
"""

import unittest
from unittest import mock

import config
from data_structures.sorting import sort_by_height
from game.character import Character
from game.game_stats import GameStats
from game.spawner import Spawner


# ===============================================================
# Start of the game: the Queue
# ===============================================================
class TestSpawnerStart(unittest.TestCase):
    def test_queue_starts_with_configured_total(self):
        spawner = Spawner()
        self.assertEqual(spawner.queue_size(), config.TOTAL_CHARACTERS)
        self.assertEqual(spawner.queue_size(), 80)

    def test_custom_total_is_used(self):
        spawner = Spawner(total=12)
        self.assertEqual(spawner.queue_size(), 12)

    def test_every_queued_symbol_is_valid(self):
        spawner = Spawner()
        for symbol in spawner.queue.to_list():
            self.assertEqual(len(symbol), 1)
            self.assertIn(symbol, config.CHARACTER_POOL)

    def test_no_active_characters_at_start(self):
        spawner = Spawner()
        self.assertEqual(spawner.active_count(), 0)
        self.assertEqual(spawner.active_characters, [])


# ===============================================================
# Spawning: Queue -> active list
# ===============================================================
class TestSpawning(unittest.TestCase):
    def test_nothing_spawns_before_the_interval(self):
        spawner = Spawner(total=5, interval=1.0)
        spawner.update(0.9)
        self.assertEqual(spawner.active_count(), 0)

    def test_character_spawns_when_interval_is_reached(self):
        spawner = Spawner(total=5, interval=1.0)
        spawner.update(1.0)
        self.assertEqual(spawner.active_count(), 1)

    def test_default_interval_is_0_8_seconds(self):
        spawner = Spawner()
        spawner.update(0.79)
        self.assertEqual(spawner.active_count(), 0)
        spawner.update(0.02)            # total 0.81 seconds
        self.assertEqual(spawner.active_count(), 1)

    def test_spawned_character_is_removed_from_queue(self):
        spawner = Spawner(total=5, interval=1.0)
        spawner.update(1.0)
        self.assertEqual(spawner.queue_size(), 4)
        self.assertEqual(spawner.active_count(), 1)

    def test_symbols_spawn_in_queue_order(self):
        spawner = Spawner(total=5, interval=1.0)
        expected = spawner.queue.to_list()          # the order inside the Queue
        for _ in range(3):
            spawner.update(1.0)
        # The oldest character has fallen the furthest, so it is first after sorting
        spawned = [character.symbol for character in spawner.active_characters]
        self.assertEqual(spawned, expected[:3])

    def test_two_spawns_in_one_big_update(self):
        spawner = Spawner(total=5, interval=1.0)
        spawner.update(2.0)
        self.assertEqual(spawner.active_count(), 2)
        self.assertEqual(spawner.queue_size(), 3)

    def test_left_over_time_is_kept(self):
        spawner = Spawner(total=5, interval=1.0)
        spawner.update(1.5)             # 1 spawn, 0.5 seconds left over
        self.assertEqual(spawner.active_count(), 1)
        spawner.update(0.5)             # 0.5 + 0.5 = 1.0 -> second spawn
        self.assertEqual(spawner.active_count(), 2)

    def test_spawning_stops_when_queue_is_empty(self):
        spawner = Spawner(total=2, interval=1.0)
        for _ in range(6):
            spawner.update(1.0)
        self.assertEqual(spawner.queue_size(), 0)
        self.assertEqual(spawner.active_count(), 2)

    def test_new_character_starts_at_spawn_y(self):
        spawner = Spawner(total=3, interval=1.0)
        spawner.update(1.0)
        self.assertEqual(spawner.active_characters[0].y, config.SPAWN_Y)

    def test_x_positions_are_valid_and_random(self):
        spawner = Spawner(total=200, interval=1.0)
        spawner.update(200.0)           # spawns all 200 at once
        x_values = [character.x for character in spawner.active_characters]
        self.assertEqual(len(x_values), 200)
        for x in x_values:
            self.assertGreaterEqual(x, config.SPAWN_X_MIN)
            self.assertLessEqual(x, config.SPAWN_X_MAX)
        self.assertGreater(len(set(x_values)), 1)   # not all the same number


# ===============================================================
# Movement
# ===============================================================
class TestMovement(unittest.TestCase):
    def test_active_character_moves_down(self):
        spawner = Spawner(total=3, interval=1.0)
        spawner.update(1.0)             # character appears at y = 0
        spawner.update(0.5)             # falls: 100 pixels/second * 0.5 s = 50
        self.assertAlmostEqual(spawner.active_characters[0].y, 50.0)

    def test_each_character_uses_its_own_speed(self):
        spawner = Spawner(total=0, interval=1.0)
        fast = Character("a", 100, 0, speed=200)
        spawner.active_characters.append(fast)
        spawner.update(0.5)             # 200 * 0.5 = 100
        self.assertAlmostEqual(fast.y, 100.0)


# ===============================================================
# Remaining characters
# ===============================================================
class TestRemaining(unittest.TestCase):
    def test_remaining_at_start_is_the_total(self):
        spawner = Spawner()
        self.assertEqual(spawner.queue_size() + spawner.active_count(), 80)

    def test_remaining_stays_the_same_while_spawning(self):
        spawner = Spawner(total=10, interval=1.0)
        for _ in range(6):
            spawner.update(1.0)
            self.assertEqual(spawner.queue_size() + spawner.active_count(), 10)

    def test_game_stats_remaining_matches_the_spawner(self):
        stats = GameStats()
        spawner = Spawner()
        self.assertEqual(stats.get_remaining(spawner.queue_size(), spawner.active_count()), 80)
        for _ in range(3):
            spawner.update(0.8)         # three spawns, one per 0.8 seconds
        self.assertEqual(spawner.active_count(), 3)
        self.assertEqual(stats.get_remaining(spawner.queue_size(), spawner.active_count()), 80)


# ===============================================================
# Sorting is really used
# ===============================================================
class TestSortingIsUsed(unittest.TestCase):
    def test_active_list_is_sorted_after_update(self):
        spawner = Spawner(total=0, interval=1.0)
        a = Character("a", 0, 100, speed=10)     # 100 + 10  = 110
        b = Character("b", 0, 50, speed=400)     # 50  + 400 = 450
        c = Character("c", 0, 300, speed=0)      # 300 + 0   = 300
        spawner.active_characters = [a, b, c]
        spawner.update(1.0)
        self.assertEqual([x.symbol for x in spawner.active_characters], ["b", "c", "a"])
        y_values = [x.y for x in spawner.active_characters]
        self.assertEqual(y_values, sorted(y_values, reverse=True))

    def test_update_calls_our_insertion_sort_on_the_active_list(self):
        spawner = Spawner(total=3, interval=1.0)
        with mock.patch("game.spawner.sort_by_height", wraps=sort_by_height) as spy:
            spawner.update(1.0)
        spy.assert_called_once()
        self.assertIs(spy.call_args[0][0], spawner.active_characters)

    def test_sorted_order_changes_the_most_urgent_character(self):
        spawner = Spawner(total=0, interval=1.0)
        high = Character("h", 0, 100, speed=0)
        low = Character("l", 0, 300, speed=0)
        spawner.active_characters = [high, low]      # NOT sorted
        self.assertIs(spawner.get_most_urgent(), high)   # wrong answer on an unsorted list
        spawner.update(0.0)                          # update sorts the list
        self.assertIs(spawner.get_most_urgent(), low)    # right answer after sorting


# ===============================================================
# get_most_urgent()
# ===============================================================
class TestMostUrgent(unittest.TestCase):
    def make_spawner(self, *y_values):
        """Spawner with no queue and characters a, b, c... at the given y values.
        Speed 0, so update() only sorts them."""
        spawner = Spawner(total=0, interval=1.0)
        for i, y in enumerate(y_values):
            spawner.active_characters.append(Character(chr(ord("a") + i), 0, y, speed=0))
        spawner.update(0.0)
        return spawner

    def test_none_when_there_are_no_characters(self):
        self.assertIsNone(Spawner(total=0).get_most_urgent())

    def test_returns_the_first_character_of_the_sorted_list(self):
        spawner = self.make_spawner(100, 300, 200)
        most_urgent = spawner.get_most_urgent()
        self.assertEqual(most_urgent.y, 300)
        self.assertIs(most_urgent, spawner.active_characters[0])

    def test_skips_characters_that_crossed_the_dead_bar(self):
        # 700 and 650 are below the Dead Bar (y = 600). 400 is the first one above it.
        spawner = self.make_spawner(100, 700, 400, 650)
        self.assertEqual([c.y for c in spawner.active_characters], [700, 650, 400, 100])
        self.assertEqual(spawner.get_most_urgent().y, 400)

    def test_character_exactly_on_the_dead_bar_counts_as_crossed(self):
        spawner = self.make_spawner(config.DEAD_BAR_Y, 599.5)
        self.assertEqual(spawner.get_most_urgent().y, 599.5)

    def test_none_when_every_character_crossed_the_dead_bar(self):
        spawner = self.make_spawner(650, 700)
        self.assertIsNone(spawner.get_most_urgent())


if __name__ == "__main__":
    unittest.main()