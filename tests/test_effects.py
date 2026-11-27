"""
test_effects.py
Tests for the Effects class (Milestone 9). It has no Pygame code,
so these tests need no window.
"""

import unittest

import config
from game.effects import Effects


class TestEffectsStart(unittest.TestCase):
    def test_new_effects_are_all_off(self):
        effects = Effects()
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.get_hits_highlight(), 0.0)
        self.assertEqual(effects.get_wrong_flash(), 0.0)
        self.assertEqual(effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(effects.get_misses_highlight(), 0.0)
        self.assertEqual(effects.floating_texts, [])
        self.assertIsNone(effects.last_wrong_key)

    def test_hit_starts_flash_highlight_and_floating_text(self):
        effects = Effects()
        effects.trigger_hit(120, 300)
        self.assertEqual(effects.get_hit_flash(), 1.0)
        self.assertEqual(effects.get_hits_highlight(), 1.0)
        self.assertEqual(len(effects.floating_texts), 1)

    def test_hit_does_not_start_other_effects(self):
        effects = Effects()
        effects.trigger_hit(120, 300)
        self.assertEqual(effects.get_wrong_flash(), 0.0)
        self.assertEqual(effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(effects.get_misses_highlight(), 0.0)

    def test_floating_text_is_plus_one_at_the_character_position(self):
        effects = Effects()
        effects.trigger_hit(120, 300)
        floating = effects.floating_texts[0]
        self.assertEqual(floating.text, "+1")
        self.assertEqual(floating.x, 120)
        self.assertEqual(floating.y, 300)

    def test_wrong_key_starts_flash_and_remembers_the_key(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        self.assertEqual(effects.get_wrong_flash(), 1.0)
        self.assertEqual(effects.last_wrong_key, "z")

    def test_last_wrong_key_is_the_newest_one(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        effects.trigger_wrong_key("Q")
        self.assertEqual(effects.last_wrong_key, "Q")

    def test_wrong_key_does_not_start_other_effects(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(effects.floating_texts, [])

    def test_miss_starts_dead_bar_and_misses_highlight(self):
        effects = Effects()
        effects.trigger_miss()
        self.assertEqual(effects.get_dead_bar_flash(), 1.0)
        self.assertEqual(effects.get_misses_highlight(), 1.0)

    def test_miss_does_not_start_hit_or_wrong_effects(self):
        effects = Effects()
        effects.trigger_miss()
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.get_hits_highlight(), 0.0)
        self.assertEqual(effects.get_wrong_flash(), 0.0)
        self.assertEqual(effects.floating_texts, [])


class TestEffectsUpdate(unittest.TestCase):
    def test_strength_goes_down_with_dt(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        effects.update(config.EFFECT_WRONG_FLASH_SECONDS / 2)
        self.assertAlmostEqual(effects.get_wrong_flash(), 0.5)

    def test_effect_ends_and_never_goes_below_zero(self):
        effects = Effects()
        effects.trigger_hit(100, 100)
        effects.trigger_wrong_key("z")
        effects.trigger_miss()
        effects.update(10.0)
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.get_hits_highlight(), 0.0)
        self.assertEqual(effects.get_wrong_flash(), 0.0)
        self.assertEqual(effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(effects.get_misses_highlight(), 0.0)

    def test_a_new_trigger_restarts_the_timer(self):
        effects = Effects()
        effects.trigger_miss()
        effects.update(0.3)
        effects.trigger_miss()
        self.assertEqual(effects.get_dead_bar_flash(), 1.0)

    def test_update_with_no_effects_does_nothing(self):
        effects = Effects()
        effects.update(0.1)
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.floating_texts, [])

    def test_floating_text_moves_through_its_life(self):
        effects = Effects()
        effects.trigger_hit(100, 100)
        floating = effects.floating_texts[0]
        self.assertEqual(floating.get_progress(), 0.0)
        effects.update(config.EFFECT_FLOAT_SECONDS / 2)
        self.assertAlmostEqual(floating.get_progress(), 0.5)
        self.assertEqual(len(effects.floating_texts), 1)

    def test_floating_text_is_removed_when_finished(self):
        effects = Effects()
        effects.trigger_hit(100, 100)
        effects.update(config.EFFECT_FLOAT_SECONDS + 0.01)
        self.assertEqual(effects.floating_texts, [])

    def test_two_hits_make_two_floating_texts_that_finish_separately(self):
        effects = Effects()
        effects.trigger_hit(100, 100)
        effects.update(config.EFFECT_FLOAT_SECONDS / 2)
        effects.trigger_hit(300, 200)
        self.assertEqual(len(effects.floating_texts), 2)
        effects.update(config.EFFECT_FLOAT_SECONDS / 2 + 0.01)
        self.assertEqual(len(effects.floating_texts), 1)
        self.assertEqual(effects.floating_texts[0].x, 300)

    def test_last_wrong_key_stays_after_the_flash_ends(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        effects.update(10.0)
        self.assertEqual(effects.last_wrong_key, "z")


class TestEffectsClear(unittest.TestCase):
    def test_clear_stops_everything(self):
        effects = Effects()
        effects.trigger_hit(100, 100)
        effects.trigger_wrong_key("z")
        effects.trigger_miss()
        effects.clear()
        self.assertEqual(effects.get_hit_flash(), 0.0)
        self.assertEqual(effects.get_hits_highlight(), 0.0)
        self.assertEqual(effects.get_wrong_flash(), 0.0)
        self.assertEqual(effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(effects.get_misses_highlight(), 0.0)
        self.assertEqual(effects.floating_texts, [])
        self.assertIsNone(effects.last_wrong_key)


if __name__ == "__main__":
    unittest.main()