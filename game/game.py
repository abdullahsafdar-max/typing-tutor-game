"""
game.py
The "boss" of the game. It opens the window, runs the main loop,
reads keyboard and mouse events, and connects GameState, GameStats and Renderer.
"""

import pygame

import config
from game.game_state import GameState
from game.game_stats import GameStats
from game.renderer import Renderer
from game.spawner import Spawner
from game.typing_handler import TypingHandler


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.state = GameState()        # which screen we are on
        self.stats = GameStats()        # created now, but its timer is NOT running yet
        self.spawner = None             # created when the game starts (see start_playing)
        self.typing_handler = None      # created together with the spawner
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
                    self.start_playing()               # only does something in the menu
                elif self.state.is_playing():
                    # event.unicode is the typed text. It already includes Shift and
                    # Caps Lock ("A" for Shift+a). It is "" for keys like Shift or Ctrl.
                    self.typing_handler.handle_key(event.unicode)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   # left click
                if self.state.is_menu() and self.renderer.start_button_rect.collidepoint(event.pos):
                    self.start_playing()

    def start_playing(self):
        """Move from the menu to the Playing screen and prepare a fresh Spawner.
        start_game() returns True only when the state really changed,
        so pressing ENTER again while playing does NOT create a new Spawner."""
        if self.state.start_game():
            self.spawner = Spawner()    # new Queue of 80 random characters
            self.typing_handler = TypingHandler(self.spawner, self.stats)

    def update(self, dt):
        """Change the game data once per frame.
        Typing is handled in handle_events. Later: timer and Dead Bar (Milestone 8)."""
        if self.state.is_playing():
            self.spawner.update(dt)     # move, spawn and sort the characters

    def draw(self):
        if self.state.is_menu():
            self.renderer.draw_menu(pygame.mouse.get_pos())
        elif self.state.is_playing():
            remaining = self.stats.get_remaining(self.spawner.queue_size(),
                                                 self.spawner.active_count())
            self.renderer.draw_playing(self.stats,
                                       self.spawner.active_characters,   # already sorted
                                       self.spawner.get_most_urgent(),
                                       remaining)
        # The Game Over screen will be added in Milestone 8
        pygame.display.flip()                          # show the finished picture