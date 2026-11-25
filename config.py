"""
config.py
All fixed settings of the game are stored here.
If you want to change speed, time, colors, or screen size,
you only change this one file.
"""

import string

# ---------------------------------------------------------------
# Window
# ---------------------------------------------------------------
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Typing Tutor Game"
FPS = 60  # frames per second

# ---------------------------------------------------------------
# Layout: play area on the left, info panel on the right
# ---------------------------------------------------------------
PANEL_WIDTH = 300
PLAY_AREA_WIDTH = WINDOW_WIDTH - PANEL_WIDTH  # 800

# ---------------------------------------------------------------
# Dead Bar and spawning positions
# ---------------------------------------------------------------
DEAD_BAR_Y = 600          # a character that reaches this y is a miss
DEAD_BAR_HEIGHT = 6       # thickness of the red line (for drawing)
SPAWN_Y = 0               # new characters start at the top
SPAWN_X_MIN = 40          # keep characters away from the left edge
SPAWN_X_MAX = PLAY_AREA_WIDTH - 40  # ...and from the right edge

# ---------------------------------------------------------------
# Game rules
# ---------------------------------------------------------------
GAME_DURATION_SECONDS = 60
TOTAL_CHARACTERS = 80            # characters placed in the Queue at start
CHARACTER_FALL_SPEED = 100       # pixels per second (fixed for now)
SPAWN_INTERVAL_SECONDS = 0.8     # time between two new characters

# ---------------------------------------------------------------
# Which characters can appear: a-z, A-Z and 0-9 (62 in total)
# ---------------------------------------------------------------
CHARACTER_POOL = string.ascii_lowercase + string.ascii_uppercase + string.digits

# ---------------------------------------------------------------
# Game states
# ---------------------------------------------------------------
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# ---------------------------------------------------------------
# Colors (R, G, B)
# ---------------------------------------------------------------
COLOR_BACKGROUND = (20, 22, 48)
COLOR_PLAY_AREA = (32, 36, 74)
COLOR_PANEL = (26, 29, 60)
COLOR_TEXT = (235, 237, 250)
COLOR_TEXT_DIM = (150, 155, 190)
COLOR_DEAD_BAR = (235, 70, 80)

COLOR_LOWERCASE = (120, 200, 255)   # light blue
COLOR_UPPERCASE = (255, 190, 90)    # orange
COLOR_DIGIT = (150, 235, 150)       # green

# ---------------------------------------------------------------
# Font sizes
# ---------------------------------------------------------------
FONT_SIZE_CHARACTER = 48
FONT_SIZE_TITLE = 56
FONT_SIZE_HUD = 26
FONT_SIZE_SMALL = 20



# ---------------------------------------------------------------
# Menu and button settings (added in Milestone 5)
# ---------------------------------------------------------------
FONT_NAME = "segoeui,arial,helvetica"   # Pygame uses the first font it finds
FONT_SIZE_BUTTON = 30

COLOR_ACCENT = (124, 108, 255)          # purple-blue (button)
COLOR_ACCENT_HOVER = (152, 138, 255)    # lighter when the mouse is over it
COLOR_CARD_BORDER = (62, 68, 128)       # thin line around cards and dividers

BUTTON_WIDTH = 260
BUTTON_HEIGHT = 64
BUTTON_RADIUS = 14                      # rounded corners