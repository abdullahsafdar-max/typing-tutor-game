"""
test_gameplay_polish.py
Tests for Milestone 9 (gameplay UI polish).

Part 1 has no Pygame code: last_hit_character, urgency levels, accuracy levels
and the timer helpers.
Part 2 uses the real Game and Renderer with Pygame's hidden "dummy" display,
so no window opens. It is skipped automatically if Pygame is not installed.
"""

import os
import unittest
from unittest import mock

import config
from game.character import (Character, URGENCY_DANGER, URGENCY_NORMAL,
                            URGENCY_WARNING)
from game.effects import Effects
from game.round_manager import END_ALL_DONE, END_TIME_UP
from game.game_stats import (ACCURACY_FAIR, ACCURACY_GOOD, ACCURACY_NONE,
                             ACCURACY_POOR, GameStats)
from game.spawner import Spawner
from game.typing_handler import (RESULT_HIT, RESULT_IGNORED, RESULT_WRONG_KEY,
                                 TypingHandler)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


def make_setup(*specs):
    """A Spawner (no Queue), a GameStats and a TypingHandler.
    `specs` are (symbol, y) pairs. The characters do not move (speed 0)."""
    spawner = Spawner(total=0, interval=1.0)
    for symbol, y in specs:
        spawner.active_characters.append(Character(symbol, 100, y, speed=0))
    spawner.update(0.0)
    stats = GameStats()
    return spawner, stats, TypingHandler(spawner, stats)


# ===============================================================
# Part 1: no Pygame
# ===============================================================
class TestLastHitCharacter(unittest.TestCase):
    def test_it_starts_as_none(self):
        _, _, handler = make_setup(("a", 100))
        self.assertIsNone(handler.last_hit_character)

    def test_a_hit_stores_the_exact_character(self):
        spawner, _, handler = make_setup(("a", 100), ("b", 300))
        target = spawner.active_characters[0]       # "b" is lower, so it is first
        self.assertEqual(handler.handle_key("b"), RESULT_HIT)
        self.assertIs(handler.last_hit_character, target)

    def test_the_stored_character_keeps_its_position(self):
        _, _, handler = make_setup(("k", 250))
        handler.handle_key("k")
        self.assertEqual(handler.last_hit_character.x, 100)
        self.assertEqual(handler.last_hit_character.y, 250)
        self.assertEqual(handler.last_hit_character.symbol, "k")

    def test_a_hit_with_duplicates_stores_the_one_with_the_greatest_y(self):
        _, _, handler = make_setup(("a", 100), ("a", 400))
        handler.handle_key("a")
        self.assertEqual(handler.last_hit_character.y, 400)

    def test_a_wrong_key_clears_it(self):
        _, _, handler = make_setup(("a", 100), ("b", 200))
        handler.handle_key("a")
        self.assertIsNotNone(handler.last_hit_character)
        self.assertEqual(handler.handle_key("z"), RESULT_WRONG_KEY)
        self.assertIsNone(handler.last_hit_character)

    def test_an_ignored_key_clears_it(self):
        _, _, handler = make_setup(("a", 100), ("b", 200))
        handler.handle_key("a")
        self.assertEqual(handler.handle_key(""), RESULT_IGNORED)
        self.assertIsNone(handler.last_hit_character)

    def test_a_second_hit_replaces_the_first(self):
        _, _, handler = make_setup(("a", 100), ("b", 200))
        handler.handle_key("a")
        handler.handle_key("b")
        self.assertEqual(handler.last_hit_character.symbol, "b")

    def test_a_key_that_hits_a_crossed_character_clears_it(self):
        _, _, handler = make_setup(("a", 100), ("x", config.DEAD_BAR_Y + 10))
        handler.handle_key("a")
        self.assertEqual(handler.handle_key("x"), RESULT_WRONG_KEY)
        self.assertIsNone(handler.last_hit_character)


class TestWrongKeyIsNotAMiss(unittest.TestCase):
    def test_wrong_keys_are_key_presses_and_never_misses(self):
        _, stats, handler = make_setup(("a", 100))
        handler.handle_key("z")
        handler.handle_key("y")
        self.assertEqual(stats.key_presses, 2)
        self.assertEqual(stats.wrong_keys, 2)
        self.assertEqual(stats.misses, 0)


class TestUrgencyLevel(unittest.TestCase):
    def level_at(self, distance):
        return Character("a", 100, config.DEAD_BAR_Y - distance, speed=0).get_urgency_level()

    def test_far_from_the_dead_bar_is_normal(self):
        self.assertEqual(self.level_at(400), URGENCY_NORMAL)

    def test_a_new_character_at_the_top_is_normal(self):
        self.assertEqual(Character("a", 100).get_urgency_level(), URGENCY_NORMAL)

    def test_just_outside_the_warning_distance_is_normal(self):
        self.assertEqual(self.level_at(config.URGENCY_WARNING_DISTANCE + 1), URGENCY_NORMAL)

    def test_exactly_at_the_warning_distance_is_warning(self):
        self.assertEqual(self.level_at(config.URGENCY_WARNING_DISTANCE), URGENCY_WARNING)

    def test_between_the_two_distances_is_warning(self):
        self.assertEqual(self.level_at(100), URGENCY_WARNING)

    def test_just_outside_the_danger_distance_is_warning(self):
        self.assertEqual(self.level_at(config.URGENCY_DANGER_DISTANCE + 1), URGENCY_WARNING)

    def test_exactly_at_the_danger_distance_is_danger(self):
        self.assertEqual(self.level_at(config.URGENCY_DANGER_DISTANCE), URGENCY_DANGER)

    def test_very_close_is_danger(self):
        self.assertEqual(self.level_at(5), URGENCY_DANGER)

    def test_the_distances_are_in_a_sensible_order(self):
        self.assertLess(config.URGENCY_DANGER_DISTANCE, config.URGENCY_WARNING_DISTANCE)

    def test_the_level_does_not_move_the_character(self):
        character = Character("a", 100, 500, speed=100)
        character.get_urgency_level()
        self.assertEqual(character.y, 500)

    def test_urgency_does_not_change_the_sorting(self):
        spawner, _, _ = make_setup(("a", 100), ("b", 580), ("c", 400))
        self.assertEqual([c.symbol for c in spawner.active_characters], ["b", "c", "a"])
        for character in spawner.active_characters:
            character.get_urgency_level()
        self.assertEqual([c.symbol for c in spawner.active_characters], ["b", "c", "a"])
        self.assertEqual(spawner.get_most_urgent().symbol, "b")


class TestAccuracyLevel(unittest.TestCase):
    def stats_with(self, hits, wrong_keys):
        stats = GameStats()
        for _ in range(hits):
            stats.record_hit("a")
        for _ in range(wrong_keys):
            stats.record_wrong_key("z")
        return stats

    def test_no_key_presses_has_no_level(self):
        self.assertEqual(GameStats().get_accuracy_level(), ACCURACY_NONE)

    def test_100_percent_is_good(self):
        self.assertEqual(self.stats_with(5, 0).get_accuracy_level(), ACCURACY_GOOD)

    def test_exactly_90_percent_is_good(self):
        self.assertEqual(self.stats_with(9, 1).get_accuracy_level(), ACCURACY_GOOD)

    def test_just_under_90_percent_is_fair(self):
        self.assertEqual(self.stats_with(8, 1).get_accuracy_level(), ACCURACY_FAIR)  # 88.9

    def test_exactly_70_percent_is_fair(self):
        self.assertEqual(self.stats_with(7, 3).get_accuracy_level(), ACCURACY_FAIR)

    def test_just_under_70_percent_is_poor(self):
        self.assertEqual(self.stats_with(2, 1).get_accuracy_level(), ACCURACY_POOR)  # 66.7

    def test_zero_percent_with_key_presses_is_poor(self):
        self.assertEqual(self.stats_with(0, 3).get_accuracy_level(), ACCURACY_POOR)

    def test_misses_alone_do_not_give_a_level(self):
        stats = GameStats()
        stats.record_miss("a")
        self.assertEqual(stats.get_accuracy_level(), ACCURACY_NONE)

    def test_the_level_does_not_change_the_accuracy_number(self):
        stats = self.stats_with(3, 1)
        stats.get_accuracy_level()
        self.assertEqual(stats.get_accuracy(), 75.0)


class TestTimerHelpers(unittest.TestCase):
    def test_full_time_is_fraction_one(self):
        self.assertEqual(GameStats().get_time_fraction(), 1.0)

    def test_half_time_is_fraction_half(self):
        stats = GameStats(duration=60)
        stats.update_timer(30)
        self.assertAlmostEqual(stats.get_time_fraction(), 0.5)

    def test_no_time_is_fraction_zero(self):
        stats = GameStats()
        stats.update_timer(1000)
        self.assertEqual(stats.get_time_fraction(), 0.0)

    def test_time_is_not_low_at_the_start(self):
        self.assertFalse(GameStats().is_time_low())

    def test_time_is_not_low_just_above_the_limit(self):
        stats = GameStats()
        stats.time_left = config.TIME_WARNING_SECONDS + 0.5
        self.assertFalse(stats.is_time_low())

    def test_time_is_low_at_the_limit(self):
        stats = GameStats()
        stats.time_left = config.TIME_WARNING_SECONDS
        self.assertTrue(stats.is_time_low())

    def test_time_is_low_at_zero(self):
        stats = GameStats()
        stats.update_timer(1000)
        self.assertTrue(stats.is_time_low())


# ===============================================================
# Part 2: the real Game and Renderer (needs Pygame)
# ===============================================================
@unittest.skipUnless(HAS_PYGAME, "Pygame is not installed")
class TestGameEffects(unittest.TestCase):
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

    def start_game(self):
        self.press(pygame.K_RETURN, "\r")

    def add_character(self, symbol, y):
        self.game.spawner.active_characters.append(Character(symbol, 100, y, speed=0))
        self.game.spawner.update(0.0)

    def finish_by_time(self):
        self.game.stats.time_left = 0.01
        self.game.update(0.05)

    # ---- effects are created and wired ----
    def test_game_has_an_effects_object_with_nothing_active(self):
        self.assertIsInstance(self.game.effects, Effects)
        self.assertEqual(self.game.effects.get_hit_flash(), 0.0)

    def test_hit_starts_the_hit_effects_at_the_character_position(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_k, "k")
        self.assertEqual(self.game.effects.get_hit_flash(), 1.0)
        self.assertEqual(self.game.effects.get_hits_highlight(), 1.0)
        floating = self.game.effects.floating_texts[0]
        self.assertEqual((floating.x, floating.y), (100, 250))

    def test_hit_does_not_start_wrong_key_or_miss_effects(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_k, "k")
        self.assertEqual(self.game.effects.get_wrong_flash(), 0.0)
        self.assertEqual(self.game.effects.get_dead_bar_flash(), 0.0)

    def test_wrong_key_starts_the_wrong_effect_and_remembers_the_key(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_z, "z")
        self.assertEqual(self.game.effects.get_wrong_flash(), 1.0)
        self.assertEqual(self.game.effects.last_wrong_key, "z")
        self.assertEqual(self.game.effects.floating_texts, [])

    def test_wrong_key_stays_a_key_press_and_not_a_miss(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_z, "z")
        self.game.update(0.1)
        self.assertEqual(self.game.stats.key_presses, 1)
        self.assertEqual(self.game.stats.wrong_keys, 1)
        self.assertEqual(self.game.stats.misses, 0)

    def test_ignored_keys_start_no_effect(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_LSHIFT, "")
        self.press(pygame.K_TAB, "\t")
        self.assertEqual(self.game.effects.get_wrong_flash(), 0.0)
        self.assertEqual(self.game.effects.get_hit_flash(), 0.0)
        self.assertIsNone(self.game.effects.last_wrong_key)

    def test_a_miss_starts_the_dead_bar_and_misses_effects(self):
        self.start_game()
        self.add_character("m", config.DEAD_BAR_Y + 20)
        self.game.update(0.0)
        self.assertEqual(self.game.stats.misses, 1)
        self.assertEqual(self.game.effects.get_dead_bar_flash(), 1.0)
        self.assertEqual(self.game.effects.get_misses_highlight(), 1.0)

    def test_no_miss_means_no_miss_effect(self):
        self.start_game()
        self.add_character("m", 200)
        self.game.update(0.1)
        self.assertEqual(self.game.stats.misses, 0)
        self.assertEqual(self.game.effects.get_dead_bar_flash(), 0.0)

    def test_effects_become_weaker_while_playing(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_z, "z")
        self.game.update(0.1)
        self.assertLess(self.game.effects.get_wrong_flash(), 1.0)

    def test_play_again_clears_the_effects(self):
        self.start_game()
        self.add_character("k", 250)
        self.press(pygame.K_k, "k")
        self.press(pygame.K_z, "z")
        self.game.effects.trigger_miss()
        self.finish_by_time()
        self.press(pygame.K_RETURN, "\r")
        self.assertTrue(self.game.state.is_playing())
        self.assertEqual(self.game.effects.get_hit_flash(), 0.0)
        self.assertEqual(self.game.effects.get_wrong_flash(), 0.0)
        self.assertEqual(self.game.effects.get_dead_bar_flash(), 0.0)
        self.assertEqual(self.game.effects.floating_texts, [])
        self.assertIsNone(self.game.effects.last_wrong_key)

    def test_main_menu_clears_the_effects(self):
        self.start_game()
        self.press(pygame.K_z, "z")
        self.game.effects.trigger_miss()
        self.finish_by_time()
        self.press(pygame.K_m, "m")
        self.assertTrue(self.game.state.is_menu())
        self.assertEqual(self.game.effects.get_wrong_flash(), 0.0)
        self.assertEqual(self.game.effects.get_dead_bar_flash(), 0.0)
        self.assertIsNone(self.game.effects.last_wrong_key)

    def test_menu_start_gives_a_clean_round(self):
        self.start_game()
        self.press(pygame.K_z, "z")
        self.finish_by_time()
        self.press(pygame.K_m, "m")
        self.start_game()
        self.assertIsNone(self.game.effects.last_wrong_key)
        self.assertEqual(self.game.effects.get_wrong_flash(), 0.0)

    # ---- every screen can be drawn ----
    def test_every_screen_can_be_drawn_with_and_without_effects(self):
        self.game.draw()                                    # menu
        self.start_game()
        self.add_character("k", 250)
        self.game.draw()                                    # playing, no effects
        self.press(pygame.K_k, "k")
        self.press(pygame.K_z, "z")
        self.game.effects.trigger_miss()
        self.game.draw()                                    # playing, all effects
        self.finish_by_time()
        self.game.draw()                                    # game over

    def test_game_over_can_be_drawn_for_every_accuracy_level(self):
        for hits, wrong in ((0, 0), (10, 0), (8, 2), (1, 4)):
            stats = GameStats()
            for _ in range(hits):
                stats.record_hit("a")
            for _ in range(wrong):
                stats.record_wrong_key("z")
            self.game.renderer.draw_game_over(stats, END_TIME_UP, 5, (0, 0))
            self.game.renderer.draw_game_over(stats, END_ALL_DONE, 0, (0, 0))

    def test_game_over_has_no_overlap_between_rows_and_buttons(self):
        # the last row of the final statistics ends above the buttons
        last_row_y = 293 + 5 * 36
        row_bottom = last_row_y + self.game.renderer.font_hud_bold.get_height() // 2
        self.assertLess(row_bottom, self.game.renderer.play_again_button_rect.top)


@unittest.skipUnless(HAS_PYGAME, "Pygame is not installed")
class TestRendererPolish(unittest.TestCase):
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
        from game.renderer import Renderer
        self.Renderer = Renderer
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.renderer = Renderer(self.screen)
        self.stats = GameStats()

    def tearDown(self):
        pygame.quit()

    def draw(self, effects, characters=()):
        self.renderer.draw_playing(self.stats, list(characters), None, 80, effects)

    def pixel(self, x, y):
        return tuple(self.screen.get_at((x, y)))[:3]

    # ---- colours chosen by type ----
    def test_event_colors_follow_the_event_type(self):
        self.assertEqual(self.Renderer._event_color("HIT 'k'"), config.COLOR_HIT)
        self.assertEqual(self.Renderer._event_color("MISS 'k'"), config.COLOR_MISS)
        self.assertEqual(self.Renderer._event_color("WRONG KEY 'z'"), config.COLOR_WRONG_KEY)

    def test_the_three_event_colors_are_different(self):
        colors = {config.COLOR_HIT, config.COLOR_MISS, config.COLOR_WRONG_KEY}
        self.assertEqual(len(colors), 3)

    def test_older_events_are_dimmer(self):
        newest = self.renderer._blend(config.COLOR_HIT, config.COLOR_PANEL, 0 * 0.1)
        oldest = self.renderer._blend(config.COLOR_HIT, config.COLOR_PANEL, 4 * 0.1)
        self.assertEqual(newest, config.COLOR_HIT)
        self.assertLess(oldest[1], newest[1])

    def test_accuracy_colors_follow_the_level(self):
        stats = GameStats()
        self.assertEqual(self.renderer._accuracy_color(stats), config.COLOR_TEXT)
        for _ in range(9):
            stats.record_hit("a")
        stats.record_wrong_key("z")
        self.assertEqual(self.renderer._accuracy_color(stats), config.COLOR_HIT)       # 90
        stats.record_wrong_key("z")
        self.assertEqual(self.renderer._accuracy_color(stats), config.COLOR_WRONG_KEY)  # 81.8
        for _ in range(5):
            stats.record_wrong_key("z")
        self.assertEqual(self.renderer._accuracy_color(stats), config.COLOR_MISS)      # 56.3

    def test_last_wrong_key_text(self):
        self.assertEqual(self.Renderer._format_key(None), "-")
        self.assertEqual(self.Renderer._format_key(" "), "Space")
        self.assertEqual(self.Renderer._format_key("z"), "z")

    def test_blend_ends_and_middle(self):
        self.assertEqual(self.Renderer._blend((0, 0, 0), (100, 200, 50), 0.0), (0, 0, 0))
        self.assertEqual(self.Renderer._blend((0, 0, 0), (100, 200, 50), 1.0), (100, 200, 50))
        self.assertEqual(self.Renderer._blend((0, 0, 0), (100, 200, 50), 0.5), (50, 100, 25))

    def test_format_time_is_unchanged(self):
        self.assertEqual(self.Renderer._format_time(60), "01:00")
        self.assertEqual(self.Renderer._format_time(9.2), "00:10")

    # ---- urgency outline colour ----
    def outline_colors(self, y):
        character = Character("k", 400, y, speed=0)
        real_rect = pygame.draw.rect
        colors = []

        def spy(surface, color, rect, *args, **kwargs):
            if kwargs.get("width") == 2 and kwargs.get("border_radius") == 10:
                colors.append(tuple(color))
            return real_rect(surface, color, rect, *args, **kwargs)

        with mock.patch.object(pygame.draw, "rect", spy):
            self.renderer.draw_playing(self.stats, [character], character, 80, Effects())
        return colors

    def test_outline_is_purple_far_from_the_dead_bar(self):
        self.assertEqual(self.outline_colors(300), [config.COLOR_URGENCY_NORMAL])

    def test_outline_is_orange_when_approaching(self):
        self.assertEqual(self.outline_colors(config.DEAD_BAR_Y - 100), [config.COLOR_URGENCY_WARNING])

    def test_outline_is_red_when_very_close(self):
        self.assertEqual(self.outline_colors(config.DEAD_BAR_Y - 30), [config.COLOR_URGENCY_DANGER])

    def test_only_the_most_urgent_character_has_an_outline(self):
        first = Character("a", 200, 560, speed=0)
        second = Character("b", 500, 300, speed=0)
        real_rect = pygame.draw.rect
        colors = []

        def spy(surface, color, rect, *args, **kwargs):
            if kwargs.get("width") == 2 and kwargs.get("border_radius") == 10:
                colors.append(tuple(color))
            return real_rect(surface, color, rect, *args, **kwargs)

        with mock.patch.object(pygame.draw, "rect", spy):
            self.renderer.draw_playing(self.stats, [first, second], first, 80, Effects())
        self.assertEqual(colors, [config.COLOR_URGENCY_DANGER])

    # ---- flashes and highlights change the picture ----
    def test_wrong_key_flash_draws_an_amber_border(self):
        self.draw(Effects())
        before = self.pixel(2, 300)
        effects = Effects()
        effects.trigger_wrong_key("z")
        self.draw(effects)
        after = self.pixel(2, 300)
        self.assertGreater(after[0], before[0] + 100)      # much more red
        self.assertGreater(after[0], after[2])             # amber: red above blue

    def test_wrong_key_border_is_gone_when_the_effect_ends(self):
        effects = Effects()
        effects.trigger_wrong_key("z")
        effects.update(10.0)
        self.draw(effects)
        self.assertEqual(self.pixel(2, 300), config.COLOR_PLAY_AREA)

    def test_hit_flash_makes_the_play_area_greener(self):
        self.draw(Effects())
        before = self.pixel(400, 300)
        effects = Effects()
        effects.trigger_hit(100, 100)
        self.draw(effects)
        after = self.pixel(400, 300)
        self.assertGreater(after[1], before[1])
        self.assertEqual(before, config.COLOR_PLAY_AREA)

    def test_miss_makes_the_dead_bar_lighter(self):
        self.draw(Effects())
        before = self.pixel(700, config.DEAD_BAR_Y + 2)
        self.assertEqual(before, config.COLOR_DEAD_BAR)
        effects = Effects()
        effects.trigger_miss()
        self.draw(effects)
        after = self.pixel(700, config.DEAD_BAR_Y + 2)
        self.assertGreater(after[1], before[1])

    def test_hits_row_gets_a_green_highlight(self):
        left = config.PLAY_AREA_WIDTH + 24 - 4      # inside the highlight, left of the text
        self.draw(Effects())
        before = self.pixel(left, 192)
        effects = Effects()
        effects.trigger_hit(100, 100)
        self.draw(effects)
        after = self.pixel(left, 192)
        self.assertGreater(after[1], before[1] + 20)

    def test_misses_row_gets_a_red_highlight(self):
        left = config.PLAY_AREA_WIDTH + 24 - 4
        self.draw(Effects())
        before = self.pixel(left, 226)
        effects = Effects()
        effects.trigger_miss()
        self.draw(effects)
        after = self.pixel(left, 226)
        self.assertGreater(after[0], before[0] + 20)

    def test_floating_plus_one_is_drawn_near_the_character_position(self):
        effects = Effects()
        effects.trigger_hit(100, 200)
        self.draw(effects)
        green_pixels = 0
        for x in range(80, 121):
            for y in range(150, 200):
                r, g, b = self.pixel(x, y)
                if g > 180 and r < 140:
                    green_pixels += 1
        self.assertGreater(green_pixels, 0)

    def test_floating_plus_one_is_gone_when_it_has_finished(self):
        effects = Effects()
        effects.trigger_hit(100, 200)
        effects.update(10.0)
        self.draw(effects)
        for x in range(80, 121):
            for y in range(150, 200):
                self.assertEqual(self.pixel(x, y), config.COLOR_PLAY_AREA)

    # ---- statistics panel ----
    def test_time_bar_is_full_at_the_start_and_shorter_later(self):
        bar_y = 155
        self.draw(Effects())
        end_x = config.WINDOW_WIDTH - 24 - 5
        self.assertEqual(self.pixel(end_x, bar_y), config.COLOR_ACCENT)
        self.stats.update_timer(config.GAME_DURATION_SECONDS / 2)
        self.draw(Effects())
        self.assertEqual(self.pixel(end_x, bar_y), config.COLOR_BAR_TRACK)

    def test_time_bar_is_red_in_the_last_seconds(self):
        self.stats.time_left = config.TIME_WARNING_SECONDS
        self.draw(Effects())
        self.assertEqual(self.pixel(config.PLAY_AREA_WIDTH + 24 + 3, 155), config.COLOR_MISS)

    def test_completed_bar_grows_with_hits_and_misses(self):
        bar_y = 425
        left = config.PLAY_AREA_WIDTH + 24 + 10
        self.draw(Effects())
        self.assertEqual(self.pixel(left, bar_y), config.COLOR_BAR_TRACK)
        for _ in range(8):
            self.stats.record_hit("a")
        self.stats.record_miss("b")
        self.stats.record_miss("c")
        self.draw(Effects())
        self.assertEqual(self.pixel(left, bar_y), config.COLOR_LOWERCASE)

    def test_panel_draws_with_every_kind_of_event(self):
        self.stats.record_hit("a")
        self.stats.record_wrong_key(" ")
        self.stats.record_miss("b")
        effects = Effects()
        effects.trigger_wrong_key(" ")
        self.draw(effects)


if __name__ == "__main__":
    unittest.main()