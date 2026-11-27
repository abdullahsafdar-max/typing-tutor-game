"""
test_game_flow.py
Tests for Milestone 8 on the real Game class: Game Over, restart and the
Main Menu. They send fake keyboard and mouse events to Game and use Pygame's
hidden "dummy" display, so no window opens.

These tests are skipped automatically if Pygame is not installed.
"""

import os
import unittest

import config
from game.character import Character
from game.round_manager import END_ALL_DONE, END_TIME_UP

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


@unittest.skipUnless(HAS_PYGAME, "Pygame is not installed")
class TestGameFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=text, mod=0))
        self.game.handle_events()

    def click(self, position, button=1):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=position, button=button))
        self.game.handle_events()

    def start_game(self):
        self.press(pygame.K_RETURN, "\r")

    def finish_by_time(self):
        self.game.stats.time_left = 0.01
        self.game.update(0.05)

    def finish_by_all_done(self):
        while not self.game.spawner.queue.is_empty():
            self.game.spawner.queue.dequeue()
        self.game.update(0.0)

    def play_a_messy_round(self):
        """Start a round and leave hits, misses, wrong keys and events behind."""
        self.start_game()
        self.game.spawner.active_characters.append(Character("k", 100, 200, speed=0))
        self.game.spawner.active_characters.append(Character("m", 100, 650, speed=0))
        self.game.spawner.update(0.0)
        self.press(pygame.K_k, "k")
        self.press(pygame.K_z, "z")
        self.game.update(0.5)

    # ---- misses through the real Game ----
    def test_game_update_counts_a_miss(self):
        self.start_game()
        self.game.spawner.active_characters.append(Character("k", 100, 590, speed=100))
        self.game.update(0.5)
        self.assertEqual(self.game.stats.misses, 1)
        self.assertEqual(self.game.stats.events.peek(), "MISS 'k'")

    def test_game_update_counts_a_miss_only_once(self):
        self.start_game()
        self.game.spawner.active_characters.append(Character("k", 100, 590, speed=100))
        for _ in range(10):
            self.game.update(0.05)
        self.assertEqual(self.game.stats.misses, 1)

    # ---- timer ----
    def test_timer_counts_down_while_playing(self):
        self.start_game()
        self.game.update(1.0)
        self.assertAlmostEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS - 1.0)

    def test_timer_does_not_run_in_the_menu(self):
        self.game.update(1.0)
        self.assertEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS)

    def test_timer_stops_on_the_game_over_screen(self):
        self.start_game()
        self.finish_by_time()
        self.game.update(1.0)
        self.assertEqual(self.game.stats.time_left, 0.0)

    # ---- Game Over ----
    def test_game_over_when_time_is_up(self):
        self.start_game()
        self.finish_by_time()
        self.assertTrue(self.game.state.is_game_over())
        self.assertEqual(self.game.end_reason, END_TIME_UP)

    def test_game_over_when_everything_is_finished(self):
        self.start_game()
        self.finish_by_all_done()
        self.assertTrue(self.game.state.is_game_over())
        self.assertEqual(self.game.end_reason, END_ALL_DONE)

    def test_game_is_not_over_at_the_start(self):
        self.start_game()
        self.game.update(0.05)
        self.assertTrue(self.game.state.is_playing())
        self.assertIsNone(self.game.end_reason)

    def test_game_over_keeps_the_final_statistics(self):
        self.play_a_messy_round()
        hits, misses = self.game.stats.hits, self.game.stats.misses
        self.finish_by_time()
        self.assertEqual(self.game.stats.hits, hits)
        self.assertEqual(self.game.stats.misses, misses)

    def test_typing_is_ignored_on_the_game_over_screen(self):
        self.start_game()
        self.finish_by_time()
        self.press(pygame.K_a, "a")
        self.assertEqual(self.game.stats.key_presses, 0)

    def test_escape_quits_on_the_game_over_screen(self):
        self.start_game()
        self.finish_by_time()
        self.press(pygame.K_ESCAPE, "\x1b")
        self.assertFalse(self.game.state.running)

    # ---- restart ----
    def test_enter_on_game_over_starts_a_new_round(self):
        self.start_game()
        self.finish_by_time()
        self.start_game()
        self.assertTrue(self.game.state.is_playing())

    def test_restart_resets_all_game_data(self):
        self.play_a_messy_round()
        old_spawner, old_stats = self.game.spawner, self.game.stats
        self.assertGreater(old_stats.hits + old_stats.misses + old_stats.key_presses, 0)
        self.finish_by_time()
        self.start_game()
        stats = self.game.stats
        self.assertIsNot(self.game.spawner, old_spawner)
        self.assertIsNot(stats, old_stats)
        self.assertEqual(stats.hits, 0)
        self.assertEqual(stats.misses, 0)
        self.assertEqual(stats.key_presses, 0)
        self.assertEqual(stats.wrong_keys, 0)
        self.assertEqual(stats.time_left, config.GAME_DURATION_SECONDS)
        self.assertTrue(stats.events.is_empty())
        self.assertEqual(self.game.spawner.queue_size(), config.TOTAL_CHARACTERS)
        self.assertEqual(self.game.spawner.active_count(), 0)
        self.assertIsNone(self.game.end_reason)

    def test_restart_connects_a_working_typing_handler(self):
        self.start_game()
        self.finish_by_time()
        self.start_game()
        self.game.spawner.active_characters.append(Character("k", 100, 200, speed=0))
        self.press(pygame.K_k, "k")
        self.assertEqual(self.game.stats.hits, 1)
        self.assertEqual(self.game.spawner.active_count(), 0)

    def test_restart_connects_a_working_round_manager(self):
        self.start_game()
        self.finish_by_time()
        self.start_game()
        self.game.update(1.0)
        self.assertAlmostEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS - 1.0)

    def test_enter_while_playing_does_not_restart(self):
        self.start_game()
        spawner_before = self.game.spawner
        self.press(pygame.K_RETURN, "\r")
        self.assertIs(self.game.spawner, spawner_before)

    def test_two_restarts_in_a_row_work(self):
        self.start_game()
        for _ in range(2):
            self.finish_by_time()
            self.start_game()
            self.assertTrue(self.game.state.is_playing())
            self.assertEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS)

    # ---- Main Menu ----
    def test_m_on_game_over_goes_to_the_menu(self):
        self.start_game()
        self.finish_by_time()
        self.press(pygame.K_m, "m")
        self.assertTrue(self.game.state.is_menu())

    def test_m_while_playing_is_a_normal_typed_key(self):
        self.start_game()
        self.game.spawner.active_characters.append(Character("m", 100, 200, speed=0))
        self.press(pygame.K_m, "m")
        self.assertTrue(self.game.state.is_playing())
        self.assertEqual(self.game.stats.hits, 1)

    def test_m_in_the_menu_does_nothing(self):
        self.press(pygame.K_m, "m")
        self.assertTrue(self.game.state.is_menu())
        self.assertEqual(self.game.stats.key_presses, 0)

    def test_a_new_game_can_start_after_going_to_the_menu(self):
        self.play_a_messy_round()
        self.finish_by_time()
        self.press(pygame.K_m, "m")
        self.start_game()
        self.assertTrue(self.game.state.is_playing())
        self.assertEqual(self.game.stats.hits, 0)
        self.assertEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS)

    # ---- mouse ----
    def test_clicking_play_again_starts_a_new_round(self):
        self.start_game()
        self.finish_by_time()
        self.click(self.game.renderer.play_again_button_rect.center)
        self.assertTrue(self.game.state.is_playing())
        self.assertEqual(self.game.stats.time_left, config.GAME_DURATION_SECONDS)

    def test_clicking_main_menu_goes_to_the_menu(self):
        self.start_game()
        self.finish_by_time()
        self.click(self.game.renderer.menu_button_rect.center)
        self.assertTrue(self.game.state.is_menu())

    def test_clicking_empty_space_on_game_over_does_nothing(self):
        self.start_game()
        self.finish_by_time()
        self.click((5, 5))
        self.assertTrue(self.game.state.is_game_over())

    def test_right_click_on_play_again_does_nothing(self):
        self.start_game()
        self.finish_by_time()
        self.click(self.game.renderer.play_again_button_rect.center, button=3)
        self.assertTrue(self.game.state.is_game_over())

    def test_start_button_still_starts_the_game_from_the_menu(self):
        self.click(self.game.renderer.start_button_rect.center)
        self.assertTrue(self.game.state.is_playing())

    def test_game_over_buttons_do_nothing_in_the_menu(self):
        self.click(self.game.renderer.play_again_button_rect.center)
        self.assertTrue(self.game.state.is_menu())

    def test_game_over_buttons_do_nothing_while_playing(self):
        self.start_game()
        spawner_before = self.game.spawner
        self.click(self.game.renderer.play_again_button_rect.center)
        self.click(self.game.renderer.menu_button_rect.center)
        self.assertTrue(self.game.state.is_playing())
        self.assertIs(self.game.spawner, spawner_before)

    # ---- drawing ----
    def test_every_screen_can_be_drawn(self):
        self.game.draw()                              # menu
        self.start_game()
        self.game.update(0.8)
        self.game.draw()                              # playing
        self.finish_by_time()
        self.game.draw()                              # game over (time up)

    def test_game_over_screen_can_be_drawn_for_both_reasons(self):
        self.start_game()
        self.finish_by_all_done()
        self.game.draw()
        self.press(pygame.K_RETURN, "\r")
        self.finish_by_time()
        self.game.draw()

    def test_game_over_screen_can_be_drawn_after_a_messy_round(self):
        self.play_a_messy_round()
        self.finish_by_time()
        self.game.draw()


if __name__ == "__main__":
    unittest.main()