import unittest

import config
from data_structures.history_stack import HistoryStack
from game.game_stats import GameStats


class TestGameStats(unittest.TestCase):
    def setUp(self):
        self.stats = GameStats()

    def test_new_stats_start_at_zero(self):
        self.assertEqual(self.stats.hits, 0)
        self.assertEqual(self.stats.misses, 0)
        self.assertEqual(self.stats.key_presses, 0)
        self.assertEqual(self.stats.wrong_keys, 0)
        self.assertTrue(self.stats.events.is_empty())

    def test_timer_starts_with_full_duration(self):
        self.assertEqual(self.stats.time_left, config.GAME_DURATION_SECONDS)

    def test_custom_duration(self):
        stats = GameStats(duration=10)
        self.assertEqual(stats.time_left, 10)

    def test_events_use_our_own_stack(self):
        self.assertIsInstance(self.stats.events, HistoryStack)

    def test_record_hit_updates_counters(self):
        self.stats.record_hit("k")
        self.assertEqual(self.stats.hits, 1)
        self.assertEqual(self.stats.key_presses, 1)
        self.assertEqual(self.stats.misses, 0)
        self.assertEqual(self.stats.wrong_keys, 0)

    def test_record_hit_pushes_event(self):
        self.stats.record_hit("k")
        self.assertEqual(self.stats.events.peek(), "HIT 'k'")

    def test_record_wrong_key_updates_counters(self):
        self.stats.record_wrong_key("x")
        self.assertEqual(self.stats.key_presses, 1)
        self.assertEqual(self.stats.wrong_keys, 1)
        self.assertEqual(self.stats.hits, 0)
        self.assertEqual(self.stats.misses, 0)

    def test_record_wrong_key_pushes_event(self):
        self.stats.record_wrong_key("x")
        self.assertEqual(self.stats.events.peek(), "WRONG KEY 'x'")

    def test_record_miss_updates_only_misses(self):
        self.stats.record_miss("R")
        self.assertEqual(self.stats.misses, 1)
        self.assertEqual(self.stats.key_presses, 0)
        self.assertEqual(self.stats.hits, 0)

    def test_record_miss_pushes_event(self):
        self.stats.record_miss("R")
        self.assertEqual(self.stats.events.peek(), "MISS 'R'")

    def test_events_are_newest_first(self):
        self.stats.record_hit("k")
        self.stats.record_miss("R")
        self.stats.record_wrong_key("x")
        self.assertEqual(
            self.stats.events.to_list(),
            ["WRONG KEY 'x'", "MISS 'R'", "HIT 'k'"],
        )
        self.assertEqual(self.stats.events.size(), 3)

    def test_accuracy_is_zero_without_key_presses(self):
        self.assertEqual(self.stats.get_accuracy(), 0.0)

    def test_accuracy_is_100_when_all_hits(self):
        self.stats.record_hit("a")
        self.stats.record_hit("b")
        self.assertEqual(self.stats.get_accuracy(), 100.0)

    def test_accuracy_with_wrong_keys(self):
        self.stats.record_hit("a")
        self.stats.record_hit("b")
        self.stats.record_hit("c")
        self.stats.record_wrong_key("x")
        self.assertEqual(self.stats.get_accuracy(), 75.0)

    def test_accuracy_is_zero_with_only_wrong_keys(self):
        self.stats.record_wrong_key("x")
        self.stats.record_wrong_key("y")
        self.assertEqual(self.stats.get_accuracy(), 0.0)

    def test_misses_do_not_change_accuracy(self):
        self.stats.record_hit("a")
        self.stats.record_miss("b")
        self.stats.record_miss("c")
        self.assertEqual(self.stats.get_accuracy(), 100.0)

    def test_accuracy_one_third(self):
        self.stats.record_hit("a")
        self.stats.record_wrong_key("x")
        self.stats.record_wrong_key("y")
        self.assertAlmostEqual(self.stats.get_accuracy(), 33.3333, places=3)

    def test_remaining_is_queue_plus_active(self):
        self.assertEqual(self.stats.get_remaining(70, 6), 76)

    def test_remaining_zero_when_nothing_left(self):
        self.assertEqual(self.stats.get_remaining(0, 0), 0)

    def test_timer_decreases(self):
        stats = GameStats(duration=10)
        stats.update_timer(2.5)
        self.assertAlmostEqual(stats.time_left, 7.5)

    def test_timer_never_goes_below_zero(self):
        stats = GameStats(duration=1)
        stats.update_timer(5)
        self.assertEqual(stats.time_left, 0.0)

    def test_time_up(self):
        stats = GameStats(duration=1)
        self.assertFalse(stats.is_time_up())
        stats.update_timer(0.5)
        self.assertFalse(stats.is_time_up())
        stats.update_timer(0.5)
        self.assertTrue(stats.is_time_up())

    def test_recent_events_limited_by_count(self):
        for symbol in "abcdefg":
            self.stats.record_hit(symbol)
        recent = self.stats.get_recent_events(3)
        self.assertEqual(recent, ["HIT 'g'", "HIT 'f'", "HIT 'e'"])

    def test_recent_events_with_fewer_events_than_count(self):
        self.stats.record_hit("a")
        self.assertEqual(self.stats.get_recent_events(5), ["HIT 'a'"])

    def test_recent_events_on_empty_stack(self):
        self.assertEqual(self.stats.get_recent_events(), [])

    def test_recent_events_do_not_change_stack(self):
        self.stats.record_hit("a")
        self.stats.record_miss("b")
        self.stats.get_recent_events(1)
        self.assertEqual(self.stats.events.size(), 2)
        self.assertEqual(self.stats.events.peek(), "MISS 'b'")


if __name__ == "__main__":
    unittest.main()