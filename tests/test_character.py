"""
test_character.py
Tests for Milestone 1: config values and the Character class.
"""

import unittest

import config
from game.character import Character


class TestConfig(unittest.TestCase):
    def test_game_rules(self):
        self.assertEqual(config.GAME_DURATION_SECONDS, 60)
        self.assertEqual(config.TOTAL_CHARACTERS, 80)

    def test_character_pool_has_62_unique_characters(self):
        # 26 lowercase + 26 uppercase + 10 digits = 62
        self.assertEqual(len(config.CHARACTER_POOL), 62)
        self.assertEqual(len(set(config.CHARACTER_POOL)), 62)


class TestCharacter(unittest.TestCase):
    def test_new_character_stores_values(self):
        c = Character("k", 200, 0, 100)
        self.assertEqual(c.symbol, "k")
        self.assertEqual(c.x, 200)
        self.assertEqual(c.y, 0)
        self.assertEqual(c.speed, 100)

    def test_move_uses_speed_and_time(self):
        c = Character("k", 200, 0, 100)
        c.move(0.5)  # 100 pixels/second * 0.5 seconds = 50 pixels
        self.assertAlmostEqual(c.y, 50.0)

    def test_has_crossed_before_dead_bar(self):
        c = Character("k", 200, 500, 100)
        self.assertFalse(c.has_crossed(600))

    def test_has_crossed_at_and_after_dead_bar(self):
        c = Character("k", 200, 600, 100)
        self.assertTrue(c.has_crossed(600))
        c.move(1)
        self.assertTrue(c.has_crossed(600))

    def test_categories(self):
        self.assertEqual(Character("a", 0).get_category(), "lower")
        self.assertEqual(Character("A", 0).get_category(), "upper")
        self.assertEqual(Character("5", 0).get_category(), "digit")


if __name__ == "__main__":
    unittest.main()