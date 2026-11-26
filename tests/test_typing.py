"""
test_typing.py
Tests for Milestone 7: typing input, Linear Search, hits and wrong keys.

Most tests need no Pygame. The last group (TestGameKeyboard) sends fake
keyboard events to the real Game class, using Pygame's hidden "dummy" display,
so no window opens.
"""

import os
import unittest

import config
from game.character import Character
from game.game_stats import GameStats
from game.spawner import Spawner
from game.typing_handler import (
    RESULT_HIT,
    RESULT_IGNORED,
    RESULT_WRONG_KEY,
    TypingHandler,
)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


def make_setup(*specs):
    """Build a Spawner (with no Queue), a GameStats and a TypingHandler.
    `specs` are (symbol, y) pairs. The characters do not move (speed 0).
    The list is sorted by spawner.update(0.0), just like in the real game."""
    spawner = Spawner(total=0, interval=1.0)
    for symbol, y in specs:
        spawner.active_characters.append(Character(symbol, 100, y, speed=0))
    spawner.update(0.0)
    stats = GameStats()
    handler = TypingHandler(spawner, stats)
    return spawner, stats, handler


# ===============================================================
# Correct key (HIT)
# ===============================================================
class TestHit(unittest.TestCase):
    def test_correct_key_increases_hits_and_key_presses(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("k")
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.key_presses, 1)

    def test_correct_key_returns_hit_result(self):
        spawner, stats, handler = make_setup(("k", 200))
        self.assertEqual(handler.handle_key("k"), RESULT_HIT)

    def test_correct_character_is_removed_from_active_list(self):
        spawner, stats, handler = make_setup(("k", 200), ("m", 300))
        target = spawner.active_characters[1]          # the "k" (y = 200)
        self.assertEqual(target.symbol, "k")
        handler.handle_key("k")
        self.assertEqual(spawner.active_count(), 1)
        self.assertNotIn(target, spawner.active_characters)
        self.assertEqual(spawner.active_characters[0].symbol, "m")

    def test_hit_creates_a_hit_event(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("k")
        self.assertEqual(stats.get_recent_events(1), ["HIT 'k'"])

    def test_digit_can_be_hit(self):
        spawner, stats, handler = make_setup(("7", 200))
        self.assertEqual(handler.handle_key("7"), RESULT_HIT)
        self.assertEqual(spawner.active_count(), 0)


# ===============================================================
# Wrong key
# ===============================================================
class TestWrongKey(unittest.TestCase):
    def test_wrong_key_increases_key_presses_only(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("z")
        self.assertEqual(stats.key_presses, 1)
        self.assertEqual(stats.wrong_keys, 1)
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 0)

    def test_wrong_key_returns_wrong_key_result(self):
        spawner, stats, handler = make_setup(("k", 200))
        self.assertEqual(handler.handle_key("z"), RESULT_WRONG_KEY)

    def test_wrong_key_creates_a_wrong_key_event(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("z")
        self.assertEqual(stats.get_recent_events(1), ["WRONG KEY 'z'"])

    def test_wrong_key_removes_nothing(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("z")
        self.assertEqual(spawner.active_count(), 1)

    def test_wrong_key_when_nothing_is_falling(self):
        spawner, stats, handler = make_setup()
        self.assertEqual(handler.handle_key("a"), RESULT_WRONG_KEY)
        self.assertEqual(stats.key_presses, 1)

    def test_misses_never_change_while_typing(self):
        spawner, stats, handler = make_setup(("k", 200), ("m", 300))
        for key in ["z", "k", "q", "m"]:
            handler.handle_key(key)
        self.assertEqual(stats.misses, 0)


# ===============================================================
# Case-sensitive matching
# ===============================================================
class TestCaseSensitive(unittest.TestCase):
    def test_lowercase_key_does_not_hit_uppercase_character(self):
        spawner, stats, handler = make_setup(("A", 200))
        self.assertEqual(handler.handle_key("a"), RESULT_WRONG_KEY)
        self.assertEqual(spawner.active_count(), 1)

    def test_uppercase_key_does_not_hit_lowercase_character(self):
        spawner, stats, handler = make_setup(("a", 200))
        self.assertEqual(handler.handle_key("A"), RESULT_WRONG_KEY)
        self.assertEqual(spawner.active_count(), 1)

    def test_exact_case_hits(self):
        spawner, stats, handler = make_setup(("A", 200), ("a", 100))
        self.assertEqual(handler.handle_key("A"), RESULT_HIT)
        self.assertEqual([c.symbol for c in spawner.active_characters], ["a"])

    def test_both_cases_on_screen_are_separate(self):
        spawner, stats, handler = make_setup(("a", 300), ("A", 200))
        handler.handle_key("A")
        self.assertEqual([c.symbol for c in spawner.active_characters], ["a"])


# ===============================================================
# Duplicate characters
# ===============================================================
class TestDuplicates(unittest.TestCase):
    def test_duplicate_selects_the_greatest_y(self):
        spawner, stats, handler = make_setup(("a", 100), ("b", 250), ("a", 400))
        handler.handle_key("a")
        remaining = [(c.symbol, c.y) for c in spawner.active_characters]
        self.assertEqual(remaining, [("b", 250), ("a", 100)])   # the y=400 one is gone

    def test_two_hits_remove_both_duplicates_in_order(self):
        spawner, stats, handler = make_setup(("a", 100), ("a", 400))
        handler.handle_key("a")
        self.assertEqual(spawner.active_characters[0].y, 100)
        handler.handle_key("a")
        self.assertEqual(spawner.active_count(), 0)
        self.assertEqual(stats.hits, 2)

    def test_identical_duplicates_remove_only_one_exact_object(self):
        spawner, stats, handler = make_setup(("a", 200), ("a", 200))
        first, second = spawner.active_characters
        handler.handle_key("a")
        self.assertEqual(spawner.active_count(), 1)
        self.assertIs(spawner.active_characters[0], second)   # the found one (first) is gone

    def test_duplicate_choice_does_not_depend_on_the_list_order(self):
        # The list is NOT sorted here: the high "a" (y=100) comes first.
        spawner = Spawner(total=0, interval=1.0)
        spawner.active_characters.append(Character("a", 100, 100, speed=0))
        spawner.active_characters.append(Character("a", 100, 400, speed=0))
        handler = TypingHandler(spawner, GameStats())
        handler.handle_key("a")
        self.assertEqual([c.y for c in spawner.active_characters], [100])   # y=400 was removed

    def test_crossed_duplicate_is_skipped(self):
        # One "a" already passed the Dead Bar (y = 700). One "a" is still visible.
        spawner, stats, handler = make_setup(("a", 700), ("a", 200))
        handler.handle_key("a")
        self.assertEqual([c.y for c in spawner.active_characters], [700])   # visible one removed


# ===============================================================
# Characters that crossed the Dead Bar cannot be typed
# ===============================================================
class TestDeadBarRule(unittest.TestCase):
    def test_character_below_the_dead_bar_is_not_typable(self):
        spawner, stats, handler = make_setup(("a", 700))
        self.assertEqual(handler.handle_key("a"), RESULT_WRONG_KEY)
        self.assertEqual(spawner.active_count(), 1)
        self.assertEqual(stats.hits, 0)

    def test_character_exactly_on_the_dead_bar_is_not_typable(self):
        spawner, stats, handler = make_setup(("a", config.DEAD_BAR_Y))
        self.assertEqual(handler.handle_key("a"), RESULT_WRONG_KEY)

    def test_character_just_above_the_dead_bar_is_typable(self):
        spawner, stats, handler = make_setup(("a", config.DEAD_BAR_Y - 0.5))
        self.assertEqual(handler.handle_key("a"), RESULT_HIT)


# ===============================================================
# Keys that are NOT typed characters
# ===============================================================
class TestIgnoredKeys(unittest.TestCase):
    def check_ignored(self, symbol):
        spawner, stats, handler = make_setup(("a", 200))
        self.assertEqual(handler.handle_key(symbol), RESULT_IGNORED)
        self.assertEqual(stats.key_presses, 0)
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.wrong_keys, 0)
        self.assertEqual(stats.get_recent_events(5), [])    # no event on the Stack
        self.assertEqual(spawner.active_count(), 1)

    def test_shift_or_ctrl_alone_is_ignored(self):
        self.check_ignored("")          # Shift, Ctrl and Alt give an empty string

    def test_ctrl_combinations_are_ignored(self):
        self.check_ignored("\x01")      # Ctrl+A
        self.check_ignored("\x03")      # Ctrl+C

    def test_enter_is_ignored(self):
        self.check_ignored("\r")

    def test_escape_is_ignored(self):
        self.check_ignored("\x1b")

    def test_tab_and_backspace_are_ignored(self):
        self.check_ignored("\t")
        self.check_ignored("\x08")

    def test_more_than_one_character_is_ignored(self):
        self.check_ignored("ab")

    def test_is_typed_character_helper(self):
        self.assertTrue(TypingHandler.is_typed_character("a"))
        self.assertTrue(TypingHandler.is_typed_character("Z"))
        self.assertTrue(TypingHandler.is_typed_character("5"))
        self.assertTrue(TypingHandler.is_typed_character(" "))
        self.assertFalse(TypingHandler.is_typed_character(""))
        self.assertFalse(TypingHandler.is_typed_character("\r"))


# ===============================================================
# Space and punctuation: printable, so they are wrong keys
# ===============================================================
class TestSpaceAndPunctuation(unittest.TestCase):
    def test_space_is_a_wrong_key(self):
        spawner, stats, handler = make_setup(("a", 200))
        self.assertEqual(handler.handle_key(" "), RESULT_WRONG_KEY)
        self.assertEqual(stats.key_presses, 1)
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 0)
        self.assertEqual(stats.get_recent_events(1), ["WRONG KEY ' '"])

    def test_punctuation_is_a_wrong_key(self):
        spawner, stats, handler = make_setup(("a", 200))
        for symbol in ["!", ".", ",", ";", "?", "-"]:
            self.assertEqual(handler.handle_key(symbol), RESULT_WRONG_KEY)
        self.assertEqual(stats.key_presses, 6)
        self.assertEqual(spawner.active_count(), 1)


# ===============================================================
# Accuracy and Remaining
# ===============================================================
class TestAccuracyAndRemaining(unittest.TestCase):
    def test_accuracy_is_100_after_one_hit(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("k")
        self.assertAlmostEqual(stats.get_accuracy(), 100.0)

    def test_accuracy_after_one_hit_and_one_wrong_key(self):
        spawner, stats, handler = make_setup(("k", 200))
        handler.handle_key("z")         # wrong key: 0 hits / 1 press = 0%
        self.assertAlmostEqual(stats.get_accuracy(), 0.0)
        handler.handle_key("k")         # hit: 1 hit / 2 presses = 50%
        self.assertAlmostEqual(stats.get_accuracy(), 50.0)

    def test_accuracy_with_three_hits_and_one_wrong_key(self):
        spawner, stats, handler = make_setup(("a", 100), ("b", 200), ("c", 300))
        for key in ["a", "b", "x", "c"]:
            handler.handle_key(key)
        self.assertAlmostEqual(stats.get_accuracy(), 75.0)   # 3 / 4 * 100

    def test_remaining_decreases_after_a_hit(self):
        spawner = Spawner(total=80, interval=0.8)
        stats = GameStats()
        handler = TypingHandler(spawner, stats)
        spawner.update(0.8)             # one character spawns
        self.assertEqual(stats.get_remaining(spawner.queue_size(), spawner.active_count()), 80)
        handler.handle_key(spawner.active_characters[0].symbol)
        self.assertEqual(stats.get_remaining(spawner.queue_size(), spawner.active_count()), 79)

    def test_remaining_is_unchanged_by_a_wrong_key(self):
        spawner = Spawner(total=80, interval=0.8)
        stats = GameStats()
        handler = TypingHandler(spawner, stats)
        spawner.update(0.8)
        handler.handle_key(" ")
        self.assertEqual(stats.get_remaining(spawner.queue_size(), spawner.active_count()), 80)


# ===============================================================
# The list stays sorted after a hit
# ===============================================================
class TestSortedAfterHit(unittest.TestCase):
    def y_values(self, spawner):
        return [c.y for c in spawner.active_characters]

    def test_list_stays_sorted_after_removing_the_middle_character(self):
        spawner, stats, handler = make_setup(("a", 500), ("b", 300), ("c", 100))
        handler.handle_key("b")
        self.assertEqual(self.y_values(spawner), [500, 100])

    def test_list_stays_sorted_after_removing_first_and_last(self):
        spawner, stats, handler = make_setup(("a", 500), ("b", 300), ("c", 100), ("d", 50))
        handler.handle_key("a")
        handler.handle_key("d")
        self.assertEqual(self.y_values(spawner), [300, 100])

    def test_list_is_still_sorted_after_the_next_update(self):
        spawner, stats, handler = make_setup(("a", 500), ("b", 300), ("c", 100))
        handler.handle_key("b")
        spawner.update(0.5)
        ys = self.y_values(spawner)
        self.assertEqual(ys, sorted(ys, reverse=True))

    def test_most_urgent_character_changes_after_it_is_hit(self):
        spawner, stats, handler = make_setup(("a", 500), ("b", 300))
        self.assertEqual(spawner.get_most_urgent().symbol, "a")
        handler.handle_key("a")
        self.assertEqual(spawner.get_most_urgent().symbol, "b")


# ===============================================================
# The new Spawner helper methods
# ===============================================================
class TestSpawnerHelpers(unittest.TestCase):
    def test_typable_characters_skip_the_crossed_ones(self):
        spawner, stats, handler = make_setup(("a", 700), ("b", 650), ("c", 400), ("d", 100))
        typable = spawner.get_typable_characters()
        self.assertEqual([c.symbol for c in typable], ["c", "d"])

    def test_typable_characters_when_none_crossed(self):
        spawner, stats, handler = make_setup(("a", 400), ("b", 100))
        self.assertEqual(len(spawner.get_typable_characters()), 2)

    def test_typable_characters_when_all_crossed_or_empty(self):
        spawner, stats, handler = make_setup(("a", 700))
        self.assertEqual(spawner.get_typable_characters(), [])
        self.assertEqual(Spawner(total=0).get_typable_characters(), [])

    def test_typable_characters_does_not_change_the_active_list(self):
        spawner, stats, handler = make_setup(("a", 700), ("b", 100))
        spawner.get_typable_characters()
        self.assertEqual(spawner.active_count(), 2)

    def test_remove_character_removes_the_exact_object(self):
        spawner, stats, handler = make_setup(("a", 300), ("b", 100))
        target = spawner.active_characters[0]
        self.assertTrue(spawner.remove_character(target))
        self.assertEqual([c.symbol for c in spawner.active_characters], ["b"])

    def test_remove_character_that_is_not_in_the_list(self):
        spawner, stats, handler = make_setup(("a", 300))
        stranger = Character("a", 100, 300, speed=0)       # looks the same, but is another object
        self.assertFalse(spawner.remove_character(stranger))
        self.assertEqual(spawner.active_count(), 1)


# ===============================================================
# Keyboard events through the real Game class (hidden display)
# ===============================================================
@unittest.skipUnless(HAS_PYGAME, "pygame is not installed")
class TestGameKeyboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use Pygame's "dummy" drivers so no window opens and no sound is needed
        cls.old_video = os.environ.get("SDL_VIDEODRIVER")
        cls.old_audio = os.environ.get("SDL_AUDIODRIVER")
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

    @classmethod
    def tearDownClass(cls):
        for name, old in (("SDL_VIDEODRIVER", cls.old_video), ("SDL_AUDIODRIVER", cls.old_audio)):
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old

    def setUp(self):
        from game.game import Game
        self.game = Game()
        pygame.event.clear()

    def tearDown(self):
        pygame.quit()

    # ---- helpers ----
    def press(self, key, text=""):
        """Send one fake key press to the game and let the game read it."""
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=text, mod=0))
        self.game.handle_events()

    def start_game(self):
        self.press(pygame.K_RETURN, "\r")

    def add_character(self, symbol, y):
        self.game.spawner.active_characters.append(Character(symbol, 100, y, speed=0))
        self.game.spawner.update(0.0)          # sort, like the real game loop does

    # ---- tests ----
    def test_escape_quits_the_game(self):
        self.press(pygame.K_ESCAPE, "\x1b")
        self.assertFalse(self.game.state.running)

    def test_escape_quits_while_playing(self):
        self.start_game()
        self.press(pygame.K_ESCAPE, "\x1b")
        self.assertFalse(self.game.state.running)

    def test_window_close_button_quits_the_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.game.handle_events()
        self.assertFalse(self.game.state.running)

    def test_enter_starts_the_game_and_is_not_a_key_press(self):
        self.start_game()
        self.assertTrue(self.game.state.is_playing())
        self.assertIsNotNone(self.game.spawner)
        self.assertEqual(self.game.stats.key_presses, 0)
        self.assertEqual(self.game.stats.get_recent_events(5), [])

    def test_enter_while_playing_is_not_a_key_press(self):
        self.start_game()
        spawner_before = self.game.spawner
        self.press(pygame.K_RETURN, "\r")
        self.assertIs(self.game.spawner, spawner_before)
        self.assertEqual(self.game.stats.key_presses, 0)

    def test_typing_on_the_menu_is_ignored(self):
        self.press(pygame.K_a, "a")
        self.assertEqual(self.game.stats.key_presses, 0)
        self.assertTrue(self.game.state.is_menu())

    def test_typing_the_right_key_hits_the_character(self):
        self.start_game()
        self.add_character("k", 200)
        self.press(pygame.K_k, "k")
        self.assertEqual(self.game.stats.hits, 1)
        self.assertEqual(self.game.spawner.active_count(), 0)

    def test_typing_a_wrong_key_counts_a_key_press(self):
        self.start_game()
        self.add_character("k", 200)
        self.press(pygame.K_z, "z")
        self.assertEqual(self.game.stats.key_presses, 1)
        self.assertEqual(self.game.stats.wrong_keys, 1)
        self.assertEqual(self.game.stats.misses, 0)
        self.assertEqual(self.game.spawner.active_count(), 1)

    def test_shift_and_ctrl_key_events_are_ignored(self):
        self.start_game()
        self.add_character("k", 200)
        self.press(pygame.K_LSHIFT, "")
        self.press(pygame.K_RSHIFT, "")
        self.press(pygame.K_LCTRL, "")
        self.assertEqual(self.game.stats.key_presses, 0)

    def test_shift_plus_letter_is_case_sensitive(self):
        self.start_game()
        self.add_character("A", 200)
        self.press(pygame.K_a, "a")             # no Shift: "a"
        self.assertEqual(self.game.stats.hits, 0)
        self.press(pygame.K_a, "A")             # with Shift: "A"
        self.assertEqual(self.game.stats.hits, 1)

    def test_spawning_and_typing_work_together(self):
        self.start_game()
        self.game.update(0.8)                   # one character spawns
        self.assertEqual(self.game.spawner.active_count(), 1)
        symbol = self.game.spawner.active_characters[0].symbol
        self.press(pygame.K_F1, symbol)         # key code does not matter, the text does
        stats = self.game.stats
        self.assertEqual(stats.hits, 1)
        self.assertEqual(stats.get_remaining(self.game.spawner.queue_size(),
                                             self.game.spawner.active_count()), 79)

    def test_timer_is_not_started(self):
        self.start_game()
        self.game.update(1.0)
        self.add_character("k", 200)
        self.press(pygame.K_k, "k")
        self.assertEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS)


if __name__ == "__main__":
    unittest.main()