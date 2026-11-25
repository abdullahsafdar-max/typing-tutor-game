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


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        self.state = GameState()        # which screen we are on
        self.stats = GameStats()        # created now, but its timer is NOT running yet
        self.renderer = Renderer(self.screen)

    def run(self):
        """The main loop. It repeats until the state says the game must stop."""
        while self.state.running:
            dt = self.clock.tick(config.FPS) / 1000   # seconds since the last frame
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
                    self.state.start_game()            # only does something in the menu

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   # left click
                if self.state.is_menu() and self.renderer.start_button_rect.collidepoint(event.pos):
                    self.state.start_game()

    def update(self, dt):
        """Nothing to update yet.
        Later: spawner (Milestone 6), typing input (7), timer and Dead Bar (8)."""
        pass

    def draw(self):
        if self.state.is_menu():
            self.renderer.draw_menu(pygame.mouse.get_pos())
        elif self.state.is_playing():
            self.renderer.draw_playing(self.stats)
        # The Game Over screen will be added in Milestone 8
        pygame.display.flip()                          # show the finished picture