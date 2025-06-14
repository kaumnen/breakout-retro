"""Laser entity for the laser paddle power-up."""

import pygame
from ..utils.constants import SCREEN_HEIGHT, WHITE


class Laser:
    """Laser shot fired from the paddle."""
    
    def __init__(self, x: float, y: float):
        """Initialize a laser shot.
        
        Args:
            x: Starting X position
            y: Starting Y position
        """
        self.x = float(x)
        self.y = float(y)
        self.width = 3
        self.height = 10
        self.speed = 8  # Pixels per frame at 60fps
        
        # Create pygame rect for collision detection
        self.rect = pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)
        
        self.active = True
    
    def update(self, dt: float):
        """Update laser position.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return
        
        # Move upward
        self.y -= self.speed * dt * 60
        
        # Update rect position
        self.rect.x = int(self.x - self.width // 2)
        self.rect.y = int(self.y)
        
        # Deactivate if off screen
        if self.y + self.height < 0:
            self.active = False
    
    def draw(self, screen: pygame.Surface):
        """Draw the laser shot.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.active:
            return
        
        # Draw laser beam
        pygame.draw.rect(screen, (255, 255, 0), self.rect)  # Yellow laser
        pygame.draw.rect(screen, WHITE, self.rect, 1)  # White outline
        
        # Add glow effect
        glow_rect = pygame.Rect(self.rect.x - 1, self.rect.y - 1, self.width + 2, self.height + 2)
        pygame.draw.rect(screen, (255, 255, 100), glow_rect, 1)
    
    def is_off_screen(self) -> bool:
        """Check if laser is off screen.
        
        Returns:
            True if laser is above screen
        """
        return self.y + self.height < 0
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle.
        
        Returns:
            Pygame Rect for collision detection
        """
        return self.rect
