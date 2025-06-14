"""Power-up entity for the Breakout game."""

import pygame
import random
import math
from ..utils.constants import (
    POWERUP_FALL_SPEED, POWERUP_SIZE, POWERUP_COLORS, POWERUP_WEIGHTS,
    POWERUP_MULTIBALL, POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE,
    POWERUP_LASER_PADDLE, POWERUP_STICKY_PADDLE, POWERUP_EXTRA_LIFE,
    POWERUP_SLOW_BALL, SCREEN_HEIGHT, WHITE, BLACK
)


class PowerUp:
    """Falling power-up that provides special abilities."""
    
    def __init__(self, x: float, y: float, powerup_type: str = None):
        """Initialize a power-up.
        
        Args:
            x: X position
            y: Y position
            powerup_type: Type of power-up (random if None)
        """
        self.x = float(x)
        self.y = float(y)
        self.size = POWERUP_SIZE
        self.fall_speed = POWERUP_FALL_SPEED
        
        # Random power-up type if not specified
        if powerup_type is None:
            # Use weighted random selection
            powerup_types = list(POWERUP_WEIGHTS.keys())
            weights = list(POWERUP_WEIGHTS.values())
            self.type = random.choices(powerup_types, weights=weights)[0]
        else:
            self.type = powerup_type
        
        self.color = POWERUP_COLORS.get(self.type, WHITE)
        
        # Create pygame rect for collision detection
        self.rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
        
        # Animation
        self.rotation = 0
        self.pulse_timer = 0
        self.collected = False
    
    def update(self, dt: float):
        """Update power-up position and animation.
        
        Args:
            dt: Delta time in seconds
        """
        if self.collected:
            return
        
        # Fall down
        self.y += self.fall_speed * dt * 60
        
        # Update rect position
        self.rect.x = int(self.x - self.size // 2)
        self.rect.y = int(self.y - self.size // 2)
        
        # Animation
        self.rotation += 90 * dt  # Rotate 90 degrees per second
        self.pulse_timer += dt * 3  # Pulse effect
    
    def draw(self, screen: pygame.Surface):
        """Draw the power-up with animations.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.collected:
            return
        
        # Pulse effect
        pulse_scale = 1.0 + 0.1 * math.sin(self.pulse_timer)
        current_size = int(self.size * pulse_scale)
        
        # Create surface for rotation
        powerup_surface = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
        
        # Draw power-up shape based on type
        center = current_size // 2
        
        if self.type == POWERUP_MULTIBALL:
            # Draw multiple circles
            pygame.draw.circle(powerup_surface, self.color, (center, center), center - 2)
            pygame.draw.circle(powerup_surface, WHITE, (center - 4, center - 4), 3)
            pygame.draw.circle(powerup_surface, WHITE, (center + 4, center + 4), 3)
        
        elif self.type == POWERUP_LARGE_PADDLE:
            # Draw wide rectangle
            pygame.draw.rect(powerup_surface, self.color, 
                           (2, center - 3, current_size - 4, 6))
            pygame.draw.rect(powerup_surface, WHITE, 
                           (2, center - 3, current_size - 4, 6), 2)
        
        elif self.type == POWERUP_SMALL_PADDLE:
            # Draw narrow rectangle
            pygame.draw.rect(powerup_surface, self.color, 
                           (center - 6, center - 2, 12, 4))
            pygame.draw.rect(powerup_surface, WHITE, 
                           (center - 6, center - 2, 12, 4), 2)
        
        elif self.type == POWERUP_LASER_PADDLE:
            # Draw paddle with laser lines
            pygame.draw.rect(powerup_surface, self.color, 
                           (4, center - 2, current_size - 8, 4))
            pygame.draw.line(powerup_surface, WHITE, 
                           (center - 3, 4), (center - 3, center - 4), 2)
            pygame.draw.line(powerup_surface, WHITE, 
                           (center + 3, 4), (center + 3, center - 4), 2)
        
        elif self.type == POWERUP_STICKY_PADDLE:
            # Draw paddle with sticky dots
            pygame.draw.rect(powerup_surface, self.color, 
                           (4, center - 2, current_size - 8, 4))
            for i in range(3):
                x = 6 + i * 4
                pygame.draw.circle(powerup_surface, WHITE, (x, center), 1)
        
        elif self.type == POWERUP_EXTRA_LIFE:
            # Draw heart shape
            pygame.draw.circle(powerup_surface, self.color, (center - 3, center - 2), 4)
            pygame.draw.circle(powerup_surface, self.color, (center + 3, center - 2), 4)
            points = [
                (center, center + 6),
                (center - 6, center + 1),
                (center + 6, center + 1)
            ]
            pygame.draw.polygon(powerup_surface, self.color, points)
        
        elif self.type == POWERUP_SLOW_BALL:
            # Draw clock-like circle
            pygame.draw.circle(powerup_surface, self.color, (center, center), center - 2)
            pygame.draw.circle(powerup_surface, WHITE, (center, center), center - 2, 2)
            # Clock hands
            pygame.draw.line(powerup_surface, WHITE, 
                           (center, center), (center, center - 5), 2)
            pygame.draw.line(powerup_surface, WHITE, 
                           (center, center), (center + 3, center), 2)
        
        else:
            # Default circle
            pygame.draw.circle(powerup_surface, self.color, (center, center), center - 2)
            pygame.draw.circle(powerup_surface, WHITE, (center, center), center - 2, 2)
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(powerup_surface, self.rotation)
        
        # Get the rect for the rotated surface and center it
        rotated_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        
        # Draw the rotated power-up
        screen.blit(rotated_surface, rotated_rect)
        
        # Draw power-up label
        font = pygame.font.Font(None, 16)
        label = self.get_label()
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(int(self.x), int(self.y + self.size // 2 + 15)))
        
        # Draw text background
        bg_rect = text_rect.inflate(4, 2)
        pygame.draw.rect(screen, BLACK, bg_rect)
        pygame.draw.rect(screen, WHITE, bg_rect, 1)
        
        screen.blit(text, text_rect)
    
    def get_label(self) -> str:
        """Get display label for the power-up type."""
        labels = {
            POWERUP_MULTIBALL: "MULTI",
            POWERUP_LARGE_PADDLE: "LARGE",
            POWERUP_SMALL_PADDLE: "SMALL",
            POWERUP_LASER_PADDLE: "LASER",
            POWERUP_STICKY_PADDLE: "STICKY",
            POWERUP_EXTRA_LIFE: "LIFE",
            POWERUP_SLOW_BALL: "SLOW"
        }
        return labels.get(self.type, "POWER")
    
    def is_below_screen(self) -> bool:
        """Check if power-up has fallen below the screen.
        
        Returns:
            True if power-up is below screen bottom
        """
        return self.y - self.size // 2 > SCREEN_HEIGHT
    
    def collect(self):
        """Mark power-up as collected."""
        self.collected = True
    
    def get_position(self) -> tuple:
        """Get the current position of the power-up.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
