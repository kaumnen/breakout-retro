"""Paddle entity for the Breakout game."""

import pygame
from ..utils.constants import (
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_Y_OFFSET,
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, POWERUP_DURATION
)
from ..utils.helpers import clamp


class Paddle:
    """Player-controlled paddle that bounces the ball."""
    
    def __init__(self, x: float = None, y: float = None):
        """Initialize the paddle.
        
        Args:
            x: X position (defaults to center of screen)
            y: Y position (defaults to bottom of screen with offset)
        """
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED
        
        # Set default position if not provided
        if x is None:
            x = (SCREEN_WIDTH - self.width) // 2
        if y is None:
            y = SCREEN_HEIGHT - PADDLE_Y_OFFSET
            
        self.x = float(x)
        self.y = float(y)
        
        # Create pygame rect for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Movement state
        self.moving_left = False
        self.moving_right = False
        
        # Control mode tracking
        self.last_mouse_pos = None
        self.using_keyboard = False
        
        # Power-up effects
        self.original_width = self.width
        self.active_powerups = {}  # Dict of powerup_type: remaining_time
        self.is_sticky = False
        self.has_laser = False
        
        # Laser system
        self.lasers = []
        self.laser_cooldown = 0
        self.laser_fire_rate = 0.5  # Fire every 0.5 seconds
        self.laser_shots_remaining = 0
        
        # Sticky system
        self.stuck_ball = None
        self.ball_release_timer = 0
    
    def update(self, dt: float):
        """Update paddle position based on input.
        
        Args:
            dt: Delta time in seconds
        """
        # Move based on current input state
        if self.moving_left and not self.moving_right:
            self.x -= self.speed * dt * 60  # Scale by 60 for consistent movement
        elif self.moving_right and not self.moving_left:
            self.x += self.speed * dt * 60
        
        # Keep paddle within screen bounds
        self.x = clamp(self.x, 0, SCREEN_WIDTH - self.width)
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.rect.width = self.width
        
        # Update power-up timers
        self.update_powerups(dt)
        
        # Update laser system
        self.update_lasers(dt)
        
        # Update sticky ball
        self.update_sticky_ball(dt)
    
    def handle_input(self, keys_pressed: dict, mouse_pos: tuple = None):
        """Handle keyboard and mouse input.
        
        Args:
            keys_pressed: Dictionary of currently pressed keys
            mouse_pos: Current mouse position (x, y)
        """
        # Check for keyboard input
        self.moving_left = keys_pressed.get(pygame.K_LEFT, False) or keys_pressed.get(pygame.K_a, False)
        self.moving_right = keys_pressed.get(pygame.K_RIGHT, False) or keys_pressed.get(pygame.K_d, False)
        
        # If keyboard input is active, switch to keyboard mode
        if self.moving_left or self.moving_right:
            self.using_keyboard = True
            self.last_mouse_pos = mouse_pos  # Remember current mouse position
        
        # Check if mouse has moved (only if we have a previous position to compare)
        elif mouse_pos and self.last_mouse_pos:
            mouse_moved = abs(mouse_pos[0] - self.last_mouse_pos[0]) > 5  # 5 pixel threshold
            if mouse_moved:
                self.using_keyboard = False
                self.last_mouse_pos = mouse_pos
        
        # Update last mouse position if we don't have one yet
        elif mouse_pos and self.last_mouse_pos is None:
            self.last_mouse_pos = mouse_pos
        
        # Mouse input only if not using keyboard and mouse has moved
        if mouse_pos and not self.using_keyboard:
            target_x = mouse_pos[0] - self.width // 2
            target_x = clamp(target_x, 0, SCREEN_WIDTH - self.width)
            
            # Smooth movement towards mouse position
            diff = target_x - self.x
            if abs(diff) > 2:  # Dead zone to prevent jittering
                self.x += diff * 0.15  # Smooth interpolation
    
    def draw(self, screen: pygame.Surface):
        """Draw the paddle on the screen with power-up effects.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Determine paddle color based on active power-ups
        paddle_color = WHITE
        if self.has_laser:
            paddle_color = (100, 100, 255)  # Blue for laser
        elif self.is_sticky:
            paddle_color = (255, 100, 255)  # Magenta for sticky
        
        # Draw main paddle
        pygame.draw.rect(screen, paddle_color, self.rect)
        
        # Add a subtle border for better visibility
        border_color = (200, 200, 200) if paddle_color == WHITE else WHITE
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw power-up indicators
        if self.has_laser:
            # Draw laser indicators
            laser_y = self.rect.top - 5
            for i in range(3):
                x = self.rect.left + (i + 1) * self.width // 4
                pygame.draw.line(screen, (255, 255, 0), (x, laser_y), (x, laser_y - 10), 2)
        
        if self.is_sticky:
            # Draw sticky dots
            for i in range(5):
                x = self.rect.left + (i + 1) * self.width // 6
                pygame.draw.circle(screen, (255, 255, 255), (x, self.rect.centery), 2)
        
        # Draw lasers
        for laser in self.lasers:
            laser.draw(screen)
    
    def get_center(self) -> tuple:
        """Get the center position of the paddle.
        
        Returns:
            Tuple of (x, y) center coordinates
        """
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def get_top_center(self) -> tuple:
        """Get the top center position of the paddle.
        
        Returns:
            Tuple of (x, y) coordinates of the top center
        """
        return (self.x + self.width // 2, self.y)
    
    def get_collision_factor(self, ball_x: float) -> float:
        """Calculate collision factor based on where ball hits paddle.
        
        This affects the angle at which the ball bounces off the paddle.
        
        Args:
            ball_x: X position of the ball
            
        Returns:
            Factor between -1.0 and 1.0 indicating hit position
            -1.0 = far left, 0.0 = center, 1.0 = far right
        """
        paddle_center = self.x + self.width // 2
        relative_pos = ball_x - paddle_center
        return clamp(relative_pos / (self.width // 2), -1.0, 1.0)
    
    def apply_powerup(self, powerup_type: str):
        """Apply a power-up effect to the paddle.
        
        Args:
            powerup_type: Type of power-up to apply
        """
        from ..utils.constants import (
            POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE, 
            POWERUP_LASER_PADDLE, POWERUP_STICKY_PADDLE
        )
        
        if powerup_type == POWERUP_LARGE_PADDLE:
            self.width = int(self.original_width * 1.5)
            self.active_powerups[powerup_type] = POWERUP_DURATION
        
        elif powerup_type == POWERUP_SMALL_PADDLE:
            self.width = int(self.original_width * 0.7)
            self.active_powerups[powerup_type] = POWERUP_DURATION
        
        elif powerup_type == POWERUP_LASER_PADDLE:
            self.has_laser = True
            self.laser_shots_remaining = 20  # 20 laser shots
            self.active_powerups[powerup_type] = POWERUP_DURATION
        
        elif powerup_type == POWERUP_STICKY_PADDLE:
            self.is_sticky = True
            self.active_powerups[powerup_type] = POWERUP_DURATION
    
    def update_powerups(self, dt: float):
        """Update power-up timers and remove expired effects.
        
        Args:
            dt: Delta time in seconds
        """
        from ..utils.constants import (
            POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE, 
            POWERUP_LASER_PADDLE, POWERUP_STICKY_PADDLE
        )
        
        expired_powerups = []
        
        for powerup_type, remaining_time in self.active_powerups.items():
            remaining_time -= dt
            
            if remaining_time <= 0:
                expired_powerups.append(powerup_type)
            else:
                self.active_powerups[powerup_type] = remaining_time
        
        # Remove expired power-ups
        for powerup_type in expired_powerups:
            del self.active_powerups[powerup_type]
            
            # Reset effects
            if powerup_type in [POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE]:
                self.width = self.original_width
            elif powerup_type == POWERUP_LASER_PADDLE:
                self.has_laser = False
                self.laser_shots_remaining = 0
                self.lasers.clear()
            elif powerup_type == POWERUP_STICKY_PADDLE:
                self.is_sticky = False
                self.release_stuck_ball()
    
    def update_lasers(self, dt: float):
        """Update laser system.
        
        Args:
            dt: Delta time in seconds
        """
        # Update laser cooldown
        if self.laser_cooldown > 0:
            self.laser_cooldown -= dt
        
        # Auto-fire lasers if we have laser power-up
        if self.has_laser and self.laser_shots_remaining > 0 and self.laser_cooldown <= 0:
            self.fire_laser()
            self.laser_cooldown = self.laser_fire_rate
        
        # Update existing lasers
        for laser in self.lasers[:]:
            laser.update(dt)
            if laser.is_off_screen():
                self.lasers.remove(laser)
    
    def fire_laser(self):
        """Fire a laser shot from the paddle."""
        from .laser import Laser
        
        if self.laser_shots_remaining > 0:
            # Fire from center of paddle
            laser_x = self.x + self.width // 2
            laser_y = self.y - 5
            laser = Laser(laser_x, laser_y)
            self.lasers.append(laser)
            self.laser_shots_remaining -= 1
    
    def update_sticky_ball(self, dt: float):
        """Update sticky ball system.
        
        Args:
            dt: Delta time in seconds
        """
        if self.stuck_ball:
            # Keep ball positioned on paddle
            self.stuck_ball.x = self.x + self.width // 2
            self.stuck_ball.y = self.y - self.stuck_ball.radius - 2
            
            # Auto-release after 1 second
            self.ball_release_timer -= dt
            if self.ball_release_timer <= 0:
                self.release_stuck_ball()
    
    def stick_ball(self, ball):
        """Stick a ball to the paddle.
        
        Args:
            ball: Ball object to stick
        """
        if self.is_sticky and not self.stuck_ball:
            self.stuck_ball = ball
            self.ball_release_timer = 1.0  # Release after 1 second
            # Stop ball movement
            ball.velocity_x = 0
            ball.velocity_y = 0
    
    def release_stuck_ball(self):
        """Release the stuck ball."""
        if self.stuck_ball:
            # Give ball upward velocity
            import random
            angle = random.uniform(60, 120)  # Upward angle
            import math
            speed = 5
            self.stuck_ball.velocity_x = math.cos(math.radians(angle)) * speed
            self.stuck_ball.velocity_y = -math.sin(math.radians(angle)) * speed
            self.stuck_ball = None
            self.ball_release_timer = 0
    
    def get_lasers(self):
        """Get list of active lasers.
        
        Returns:
            List of active Laser objects
        """
        return [laser for laser in self.lasers if laser.active]
