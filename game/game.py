"""
game.py
The "boss" of the game. It opens the window, runs the main loop,
reads keyboard and mouse events, and connects GameState, GameStats,
Spawner, RoundManager and Renderer.
"""

import pygame

import config
from game.game_state import GameState
from game.game_stats import GameStats
from game.renderer import Renderer
from game.round_manager import RoundManager
from game.spawner import Spawner
from game.typing_handler import TypingHandler


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.state = GameState()        # which screen we are on
        self.stats = GameStats()        # replaced by a fresh one in every new round
        self.spawner = None             # created when a round starts (see start_new_round)
        self.typing_handler = None      # created together with the spawner
        self.round_manager = None       # created together with the spawner
        self.end_reason = None          # why the last round ended (shown on Game Over)
        self.renderer = Renderer(self.screen)

    def run(self):
        """The main loop. It repeats until the state says the game must stop."""
        while self.state.running:
            dt = self.clock.tick(config.FPS) / 1000   # seconds since the last frame
            dt = min(dt, config.MAX_FRAME_TIME)        # never count a huge frame (window freeze)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()                                  # clean exit

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:              # window X button
                self.state.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:       # ESC works in every state
                    self.state.quit()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.handle_enter()
                elif self.state.is_game_over() and event.key == pygame.K_m:
                    self.go_to_menu()                  # M = Main Menu (only on Game Over)
                elif self.state.is_playing():
                    # event.unicode is the typed text. It already includes Shift and
                    # Caps Lock ("A" for Shift+a). It is "" for keys like Shift or Ctrl.
                    self.typing_handler.handle_key(event.unicode)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   # left click
                self.handle_click(event.pos)

    def handle_enter(self):
        """ENTER starts a round from the menu, or starts a new one from Game Over.
        While playing it does nothing."""
        if self.state.is_menu():
            self.start_playing()
        elif self.state.is_game_over():
            self.play_again()

    def handle_click(self, position):
        if self.state.is_menu():
            if self.renderer.start_button_rect.collidepoint(position):
                self.start_playing()
        elif self.state.is_game_over():
            if self.renderer.play_again_button_rect.collidepoint(position):
                self.play_again()
            elif self.renderer.menu_button_rect.collidepoint(position):
                self.go_to_menu()

    def start_playing(self):
        """Menu -> Playing, with a completely new round.
        start_game() returns True only when the state really changed,
        so pressing ENTER again while playing does NOT start another round."""
        if self.state.start_game():
            self.start_new_round()

    def play_again(self):
        """Game Over -> Playing, with a completely new round."""
        if self.state.restart_game():
            self.start_new_round()

    def go_to_menu(self):
        """Game Over -> Main Menu."""
        self.state.go_to_menu()

    def start_new_round(self):
        """Create ALL game data again, so nothing is left from the last round:
        new statistics (hits, misses, timer, event Stack), a new Queue of 80
        random characters, an empty active list and a new typing handler."""
        self.stats = GameStats()
        self.spawner = Spawner()
        self.typing_handler = TypingHandler(self.spawner, self.stats)
        self.round_manager = RoundManager(self.spawner, self.stats)
        self.end_reason = None

    def update(self, dt):
        """Change the game data once per frame.
        Typing is handled in handle_events."""
        if self.state.is_playing():
            self.round_manager.update(dt)               # timer, movement, misses
            if self.round_manager.is_over():
                self.end_reason = self.round_manager.end_reason()
                self.state.end_game()                   # show the Game Over screen

    def draw(self):
        mouse_position = pygame.mouse.get_pos()
        if self.state.is_menu():
            self.renderer.draw_menu(mouse_position)
        elif self.state.is_playing():
            remaining = self.stats.get_remaining(self.spawner.queue_size(),
                                                 self.spawner.active_count())
            self.renderer.draw_playing(self.stats,
                                       self.spawner.active_characters,   # already sorted
                                       self.spawner.get_most_urgent(),
                                       remaining)
        elif self.state.is_game_over():
            remaining = self.stats.get_remaining(self.spawner.queue_size(),
                                                 self.spawner.active_count())
            self.renderer.draw_game_over(self.stats, self.end_reason, remaining,
                                         mouse_position)
        pygame.display.flip()                          # show the finished picture