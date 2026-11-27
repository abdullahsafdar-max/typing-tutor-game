"""
game_state.py
Keeps track of WHICH screen the game is on (menu, playing, game over)
and whether the game should keep running.
This file has NO Pygame code, so it is easy to test.
"""

from config import STATE_MENU, STATE_PLAYING, STATE_GAME_OVER


class GameState:
    def __init__(self):
        self.current = STATE_MENU   # the game always starts on the menu
        self.running = True         # becomes False when the game must close

    # ---- simple questions ----
    def is_menu(self):
        return self.current == STATE_MENU

    def is_playing(self):
        return self.current == STATE_PLAYING

    def is_game_over(self):
        return self.current == STATE_GAME_OVER

    # ---- actions ----
    def start_game(self):
        """Menu -> Playing. In any other state it does nothing.
        Returns True if the state really changed, otherwise False."""
        if self.current == STATE_MENU:
            self.current = STATE_PLAYING
            return True
        return False

    def end_game(self):
        """Playing -> Game Over. In any other state it does nothing.
        Returns True if the state really changed, otherwise False."""
        if self.current == STATE_PLAYING:
            self.current = STATE_GAME_OVER
            return True
        return False

    def restart_game(self):
        """Game Over -> Playing (Play Again). In any other state it does nothing.
        Returns True if the state really changed, otherwise False."""
        if self.current == STATE_GAME_OVER:
            self.current = STATE_PLAYING
            return True
        return False

    def go_to_menu(self):
        """Game Over -> Menu. In any other state it does nothing.
        Returns True if the state really changed, otherwise False."""
        if self.current == STATE_GAME_OVER:
            self.current = STATE_MENU
            return True
        return False

    def quit(self):
        """Ask the game to close. Works in every state."""
        self.running = False