"""Game constants and configuration."""

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (5, 7, 18)
WHITE = (238, 246, 255)
RED = (255, 77, 109)
GREEN = (64, 224, 163)
BLUE = (79, 140, 255)
YELLOW = (255, 211, 92)
ORANGE = (255, 142, 83)
PURPLE = (174, 108, 255)
CYAN = (64, 220, 255)

# Interface colors
BACKGROUND_TOP = (7, 10, 28)
BACKGROUND_BOTTOM = (18, 11, 43)
PANEL = (15, 21, 48)
PANEL_BORDER = (57, 75, 126)
MUTED_TEXT = (143, 161, 199)
ACCENT = (81, 236, 255)

# Paddle settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 12  # Increased from 8
PADDLE_Y_OFFSET = 50  # Distance from bottom of screen

# Ball settings
BALL_RADIUS = 8
BALL_SPEED = 6  # Increased from 4
BALL_MAX_SPEED = 14  # Increased from 10

# Brick settings
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 3
BRICK_ROWS = 8
BRICK_COLS = 10
BRICK_Y_OFFSET = 68  # Distance from top of screen

# Game settings
INITIAL_LIVES = 3
POINTS_PER_BRICK = 10

# Power-up types
POWERUP_MULTIBALL = "multiball"
POWERUP_LARGE_PADDLE = "large_paddle"
POWERUP_SMALL_PADDLE = "small_paddle"
POWERUP_LASER_PADDLE = "laser_paddle"
POWERUP_STICKY_PADDLE = "sticky_paddle"
POWERUP_EXTRA_LIFE = "extra_life"
POWERUP_SLOW_BALL = "slow_ball"

# Power-up settings
POWERUP_FALL_SPEED = 3  # Increased from 2
POWERUP_SIZE = 20
POWERUP_DURATION = 10.0  # seconds
POWERUP_DROP_CHANCE = 0.25  # Increased from 0.15 (25% chance per brick)

# Power-up weights for random selection (higher = more likely)
POWERUP_WEIGHTS = {
    POWERUP_MULTIBALL: 30,      # Most common
    POWERUP_LARGE_PADDLE: 15,
    POWERUP_SMALL_PADDLE: 8,    # Less common (negative effect)
    POWERUP_LASER_PADDLE: 12,
    POWERUP_STICKY_PADDLE: 10,
    POWERUP_EXTRA_LIFE: 20,     # Common
    POWERUP_SLOW_BALL: 15,
}

# Power-up colors
POWERUP_COLORS = {
    POWERUP_MULTIBALL: (255, 100, 100),      # Light red
    POWERUP_LARGE_PADDLE: (100, 255, 100),   # Light green
    POWERUP_SMALL_PADDLE: (255, 255, 100),   # Yellow
    POWERUP_LASER_PADDLE: (100, 100, 255),   # Light blue
    POWERUP_STICKY_PADDLE: (255, 100, 255),  # Magenta
    POWERUP_EXTRA_LIFE: (255, 215, 0),       # Gold
    POWERUP_SLOW_BALL: (0, 255, 255),        # Cyan
}

# Brick colors by row (top to bottom)
BRICK_COLORS = [
    RED,     # Row 1-2
    RED,
    ORANGE,  # Row 3-4
    ORANGE,
    YELLOW,  # Row 5-6
    YELLOW,
    GREEN,   # Row 7-8
    GREEN
]
