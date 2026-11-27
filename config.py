import string

# Window
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Typing Tutor Game"
FPS = 60  # frames per second

# Layout: play area on the left, info panel on the right
PANEL_WIDTH = 300
PLAY_AREA_WIDTH = WINDOW_WIDTH - PANEL_WIDTH  # 800

# Dead Bar and spawning positions
DEAD_BAR_Y = 600          # a character that reaches this y is a miss
DEAD_BAR_HEIGHT = 6       # thickness of the red line (for drawing)
SPAWN_Y = 0               # new characters start at the top
SPAWN_X_MIN = 40          # keep characters away from the left edge
SPAWN_X_MAX = PLAY_AREA_WIDTH - 40  # ...and from the right edge

# Game rules
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

# Font sizes
FONT_SIZE_CHARACTER = 48
FONT_SIZE_TITLE = 56
FONT_SIZE_HUD = 26
FONT_SIZE_SMALL = 20



# Menu and button settings (added in Milestone 5)
FONT_NAME = "segoeui,arial,helvetica"  
FONT_SIZE_BUTTON = 30

COLOR_ACCENT = (124, 108, 255)        
COLOR_ACCENT_HOVER = (152, 138, 255)  
COLOR_CARD_BORDER = (62, 68, 128)     

BUTTON_WIDTH = 260
BUTTON_HEIGHT = 64
BUTTON_RADIUS = 14 



CHARACTER_FONT_NAME = "consolas,couriernew,dejavusansmono,monospace"
MAX_FRAME_TIME = 0.05


# Game Over screen
COLOR_BUTTON_SECONDARY = (46, 51, 100)
COLOR_BUTTON_SECONDARY_HOVER = (62, 68, 128)


# ---------------------------------------------------------------
# Milestone 9: gameplay UI polish
# ---------------------------------------------------------------
# Feedback colors
COLOR_HIT = (90, 220, 120)            # green
COLOR_MISS = COLOR_DEAD_BAR           # red (same red as the Dead Bar)
COLOR_WRONG_KEY = (255, 175, 50)      # amber
COLOR_DEAD_BAR_FLASH = (255, 130, 140)  # lighter red for the Dead Bar highlight

# Urgency outline colors
COLOR_URGENCY_NORMAL = COLOR_ACCENT           # purple
COLOR_URGENCY_WARNING = (255, 150, 50)        # orange
COLOR_URGENCY_DANGER = (235, 70, 80)          # red

# Urgency distances: pixels between the character and the Dead Bar
URGENCY_WARNING_DISTANCE = 150   # closer than this: orange
URGENCY_DANGER_DISTANCE = 60     # closer than this: red

# How long each effect lasts, in seconds
EFFECT_HIT_FLASH_SECONDS = 0.15
EFFECT_WRONG_FLASH_SECONDS = 0.25
EFFECT_DEAD_BAR_FLASH_SECONDS = 0.40
EFFECT_STAT_HIGHLIGHT_SECONDS = 0.35
EFFECT_FLOAT_SECONDS = 0.70      # the floating +1
EFFECT_FLOAT_RISE_PIXELS = 45    # how far the +1 moves up while it fades

# Statistics panel
TIME_WARNING_SECONDS = 10        # the timer turns red at this many seconds or less
ACCURACY_GOOD_MIN = 90           # accuracy >= 90 is green
ACCURACY_FAIR_MIN = 70           # accuracy >= 70 is amber, lower is red
FONT_SIZE_TIMER = 52
COLOR_BAR_TRACK = (46, 51, 100)  # the empty part of a progress bar