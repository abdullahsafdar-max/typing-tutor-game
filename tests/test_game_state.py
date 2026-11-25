"""
test_game_state.py
Tests for the GameState class (Milestone 5). No Pygame is needed.
"""

import unittest

import config
from game.game_state import GameState


class TestGameState(unittest.TestCase):
    def setUp(self):
        self.state = GameState()

    def test_new_game_starts_in_menu_state(self):
        self.assertEqual(self.state.current, config.STATE_MENU)

    def test_new_game_is_running(self):
        self.assertTrue(self.state.running)

    def test_helper_methods_in_menu(self):
        self.assertTrue(self.state.is_menu())
        self.assertFalse(self.state.is_playing())
        self.assertFalse(self.state.is_game_over())

    def test_start_game_moves_menu_to_playing(self):
        self.state.start_game()
        self.assertEqual(self.state.current, config.STATE_PLAYING)
        self.assertTrue(self.state.is_playing())
        self.assertFalse(self.state.is_menu())

    def test_start_game_returns_true_when_state_changes(self):
        self.assertTrue(self.state.start_game())

    def test_start_game_in_playing_does_nothing(self):
        self.state.start_game()
        changed = self.state.start_game()          # second ENTER or click
        self.assertFalse(changed)
        self.assertEqual(self.state.current, config.STATE_PLAYING)

    def test_start_game_in_game_over_does_nothing(self):
        self.state.current = config.STATE_GAME_OVER
        changed = self.state.start_game()
        self.assertFalse(changed)
        self.assertEqual(self.state.current, config.STATE_GAME_OVER)

    def test_start_game_keeps_game_running(self):
        self.state.start_game()
        self.assertTrue(self.state.running)

    def test_quit_from_menu(self):
        self.state.quit()
        self.assertFalse(self.state.running)

    def test_quit_from_playing(self):
        self.state.start_game()
        self.state.quit()
        self.assertFalse(self.state.running)

    def test_quit_from_game_over(self):
        self.state.current = config.STATE_GAME_OVER
        self.state.quit()
        self.assertFalse(self.state.running)

    def test_quit_keeps_current_state(self):
        self.state.quit()
        self.assertEqual(self.state.current, config.STATE_MENU)


if __name__ == "__main__":
    unittest.main()