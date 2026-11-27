"""
test_round_manager.py
Tests for Milestone 8: misses, the timer, the end of the game and the new
GameState actions. No Pygame is needed.
"""

import unittest

import config
from game.character import Character
from game.game_state import GameState
from game.game_stats import GameStats
from game.round_manager import END_ALL_DONE, END_TIME_UP, RoundManager
from game.spawner import Spawner
from game.typing_handler import RESULT_WRONG_KEY, TypingHandler


def make_round(*specs, total=0, interval=1.0, duration=60):
    """Build a Spawner, a GameStats and a RoundManager.
    `specs` are (symbol, y, speed) triples. The Queue gets `total` random symbols."""
    spawner = Spawner(total=total, interval=interval)
    for symbol, y, speed in specs:
        spawner.active_characters.append(Character(symbol, 100, y, speed=speed))
    stats = GameStats(duration=duration)
    return spawner, stats, RoundManager(spawner, stats)


# ===============================================================
# Spawner.remove_crossed_characters
# ===============================================================
class TestRemoveCrossed(unittest.TestCase):
    def test_returns_empty_list_when_nothing_crossed(self):
        spawner, _, manager = make_round(("a", 100, 0), ("b", 300, 0))
        spawner.update(0.0)
        self.assertEqual(spawner.remove_crossed_characters(), [])
        self.assertEqual(spawner.active_count(), 2)

    def test_empty_list(self):
        spawner = Spawner(total=0)
        self.assertEqual(spawner.remove_crossed_characters(), [])

    def test_removes_only_crossed_characters(self):
        spawner, _, _ = make_round(("a", 100, 0), ("b", 650, 0), ("c", 300, 0))
        spawner.update(0.0)
        crossed = spawner.remove_crossed_characters()
        self.assertEqual([c.symbol for c in crossed], ["b"])
        self.assertEqual([c.symbol for c in spawner.active_characters], ["c", "a"])

    def test_removes_several_crossed_characters(self):
        spawner, _, _ = make_round(("a", 610, 0), ("b", 700, 0), ("c", 100, 0))
        spawner.update(0.0)
        crossed = spawner.remove_crossed_characters()
        self.assertEqual(sorted(c.symbol for c in crossed), ["a", "b"])
        self.assertEqual([c.symbol for c in spawner.active_characters], ["c"])

    def test_character_exactly_on_the_dead_bar_has_crossed(self):
        spawner, _, _ = make_round(("a", config.DEAD_BAR_Y, 0))
        spawner.update(0.0)
        self.assertEqual(len(spawner.remove_crossed_characters()), 1)

    def test_second_call_returns_nothing(self):
        spawner, _, _ = make_round(("a", 650, 0))
        spawner.update(0.0)
        spawner.remove_crossed_characters()
        self.assertEqual(spawner.remove_crossed_characters(), [])


# ===============================================================
# Misses
# ===============================================================
class TestMisses(unittest.TestCase):
    def test_crossing_the_dead_bar_counts_one_miss(self):
        spawner, stats, manager = make_round(("k", 590, 100))
        manager.update(0.5)                       # 590 + 50 = 640, crossed
        self.assertEqual(stats.misses, 1)
        self.assertEqual(spawner.active_count(), 0)

    def test_a_miss_is_counted_exactly_once(self):
        spawner, stats, manager = make_round(("k", 590, 100), total=5)
        for _ in range(100):
            manager.update(0.05)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(stats.events.to_list().count("MISS 'k'"), 1)

    def test_character_before_the_dead_bar_is_not_a_miss(self):
        _, stats, manager = make_round(("k", 100, 100))
        manager.update(0.5)
        self.assertEqual(stats.misses, 0)

    def test_miss_pushes_an_event_on_the_stack(self):
        _, stats, manager = make_round(("R", 650, 0))
        manager.update(0.0)
        self.assertEqual(stats.events.peek(), "MISS 'R'")

    def test_miss_does_not_change_key_presses_hits_or_accuracy(self):
        _, stats, manager = make_round(("R", 650, 0))
        stats.record_hit("a")
        manager.update(0.0)
        self.assertEqual(stats.key_presses, 1)
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.wrong_keys, 0)
        self.assertEqual(stats.get_accuracy(), 100.0)

    def test_several_characters_cross_in_one_frame(self):
        _, stats, manager = make_round(("a", 610, 0), ("b", 620, 0), ("c", 630, 0))
        manager.update(0.0)
        self.assertEqual(stats.misses, 3)

    def test_miss_reduces_the_remaining_count(self):
        spawner, stats, manager = make_round(("a", 650, 0), ("b", 100, 0))
        before = stats.get_remaining(spawner.queue_size(), spawner.active_count())
        manager.update(0.0)
        after = stats.get_remaining(spawner.queue_size(), spawner.active_count())
        self.assertEqual(before, 2)
        self.assertEqual(after, 1)

    def test_a_missed_character_can_not_be_typed_any_more(self):
        spawner, stats, manager = make_round(("k", 650, 0))
        handler = TypingHandler(spawner, stats)
        manager.update(0.0)
        self.assertEqual(handler.handle_key("k"), RESULT_WRONG_KEY)
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 1)

    def test_a_typed_character_is_never_a_miss(self):
        spawner, stats, manager = make_round(("k", 590, 100))
        handler = TypingHandler(spawner, stats)
        handler.handle_key("k")
        manager.update(1.0)
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.misses, 0)


# ===============================================================
# Timer
# ===============================================================
class TestTimer(unittest.TestCase):
    def test_timer_goes_down_by_dt(self):
        _, stats, manager = make_round(total=5, duration=10)
        manager.update(0.5)
        self.assertAlmostEqual(stats.time_left, 9.5)

    def test_timer_adds_up_over_many_frames(self):
        _, stats, manager = make_round(total=5, duration=10)
        for _ in range(20):
            manager.update(0.05)
        self.assertAlmostEqual(stats.time_left, 9.0)

    def test_timer_never_goes_below_zero(self):
        _, stats, manager = make_round(total=5, duration=1)
        manager.update(5)
        self.assertEqual(stats.time_left, 0.0)

    def test_round_is_not_over_while_time_is_left(self):
        _, _, manager = make_round(total=5, duration=10)
        manager.update(1.0)
        self.assertFalse(manager.is_over())
        self.assertIsNone(manager.end_reason())

    def test_round_is_over_when_time_reaches_zero(self):
        _, _, manager = make_round(total=5, duration=1)
        manager.update(1.0)
        self.assertTrue(manager.is_over())
        self.assertEqual(manager.end_reason(), END_TIME_UP)


# ===============================================================
# Game over when everything is finished
# ===============================================================
class TestAllDone(unittest.TestCase):
    def test_new_full_round_is_not_over(self):
        _, _, manager = make_round(total=config.TOTAL_CHARACTERS)
        self.assertFalse(manager.is_over())

    def test_over_when_queue_and_list_are_both_empty(self):
        _, _, manager = make_round(total=0)
        self.assertTrue(manager.is_over())
        self.assertEqual(manager.end_reason(), END_ALL_DONE)

    def test_not_over_when_only_the_queue_has_items(self):
        _, _, manager = make_round(total=3)
        self.assertFalse(manager.is_over())

    def test_not_over_when_only_the_list_has_items(self):
        _, _, manager = make_round(("a", 100, 0), total=0)
        self.assertFalse(manager.is_over())

    def test_over_after_the_last_character_is_typed(self):
        spawner, stats, manager = make_round(("a", 100, 0), total=0)
        TypingHandler(spawner, stats).handle_key("a")
        self.assertTrue(manager.is_over())
        self.assertEqual(manager.end_reason(), END_ALL_DONE)

    def test_over_after_the_last_character_is_missed(self):
        _, stats, manager = make_round(("a", 650, 0), total=0)
        manager.update(0.0)
        self.assertEqual(stats.misses, 1)
        self.assertEqual(manager.end_reason(), END_ALL_DONE)

    def test_all_done_wins_when_time_is_also_up(self):
        _, _, manager = make_round(total=0, duration=1)
        manager.update(1.0)
        self.assertEqual(manager.end_reason(), END_ALL_DONE)


# ===============================================================
# Whole rounds, simulated frame by frame
# ===============================================================
class TestFullRound(unittest.TestCase):
    def play(self, spawner, stats, manager, type_everything):
        handler = TypingHandler(spawner, stats)
        frames = 0
        while not manager.is_over() and frames < 10000:
            manager.update(0.05)
            if type_everything:
                for character in list(spawner.active_characters):
                    handler.handle_key(character.symbol)
            frames += 1
        return frames

    def test_player_who_types_nothing(self):
        spawner, stats, manager = make_round(total=config.TOTAL_CHARACTERS,
                                             interval=config.SPAWN_INTERVAL_SECONDS)
        self.play(spawner, stats, manager, type_everything=False)
        self.assertTrue(manager.is_over())
        self.assertEqual(stats.hits, 0)
        self.assertGreater(stats.misses, 0)
        total = stats.hits + stats.misses + spawner.queue_size() + spawner.active_count()
        self.assertEqual(total, config.TOTAL_CHARACTERS)

    def test_perfect_player_finishes_every_character(self):
        spawner, stats, manager = make_round(total=10, interval=0.5)
        self.play(spawner, stats, manager, type_everything=True)
        self.assertEqual(manager.end_reason(), END_ALL_DONE)
        self.assertEqual(stats.hits, 10)
        self.assertEqual(stats.misses, 0)
        self.assertEqual(stats.get_accuracy(), 100.0)

    def test_every_character_is_counted_once(self):
        spawner, stats, manager = make_round(total=20, interval=0.5)
        self.play(spawner, stats, manager, type_everything=False)
        self.assertEqual(manager.end_reason(), END_ALL_DONE)
        self.assertEqual(stats.misses, 20)

    def test_game_ends_after_about_the_game_duration(self):
        spawner, stats, manager = make_round(total=config.TOTAL_CHARACTERS,
                                             interval=config.SPAWN_INTERVAL_SECONDS)
        frames = self.play(spawner, stats, manager, type_everything=True)
        self.assertEqual(manager.end_reason(), END_TIME_UP)
        self.assertAlmostEqual(frames * 0.05, config.GAME_DURATION_SECONDS, delta=0.2)


# ===============================================================
# GameState: Game Over and restart
# ===============================================================
class TestGameStateGameOver(unittest.TestCase):
    def setUp(self):
        self.state = GameState()

    def test_end_game_moves_playing_to_game_over(self):
        self.state.start_game()
        self.assertTrue(self.state.end_game())
        self.assertTrue(self.state.is_game_over())

    def test_end_game_does_nothing_in_the_menu(self):
        self.assertFalse(self.state.end_game())
        self.assertTrue(self.state.is_menu())

    def test_end_game_does_nothing_in_game_over(self):
        self.state.start_game()
        self.state.end_game()
        self.assertFalse(self.state.end_game())
        self.assertTrue(self.state.is_game_over())

    def test_restart_moves_game_over_to_playing(self):
        self.state.start_game()
        self.state.end_game()
        self.assertTrue(self.state.restart_game())
        self.assertTrue(self.state.is_playing())

    def test_restart_does_nothing_in_the_menu_or_while_playing(self):
        self.assertFalse(self.state.restart_game())
        self.assertTrue(self.state.is_menu())
        self.state.start_game()
        self.assertFalse(self.state.restart_game())
        self.assertTrue(self.state.is_playing())

    def test_go_to_menu_moves_game_over_to_menu(self):
        self.state.start_game()
        self.state.end_game()
        self.assertTrue(self.state.go_to_menu())
        self.assertTrue(self.state.is_menu())

    def test_go_to_menu_does_nothing_while_playing(self):
        self.state.start_game()
        self.assertFalse(self.state.go_to_menu())
        self.assertTrue(self.state.is_playing())

    def test_quit_works_in_game_over(self):
        self.state.start_game()
        self.state.end_game()
        self.state.quit()
        self.assertFalse(self.state.running)


if __name__ == "__main__":
    unittest.main()