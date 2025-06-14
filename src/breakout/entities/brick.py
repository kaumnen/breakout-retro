"""Brick entity for the Breakout game."""

import pygame
import random
from ..utils.constants import (
    BRICK_WIDTH, BRICK_HEIGHT, POINTS_PER_BRICK,
    BRICK_COLORS, BLACK, POWERUP_DROP_CHANCE
)


class Brick:
    """Destructible brick that the ball can break."""
    
    def __init__(self, x: float, y: float, color: tuple = None, points: int = None, hits_required: int = 1):
        """Initialize a brick.
        
        Args:
            x: X position
            y: Y position
            color: RGB color tuple (defaults to red)
            points: Points awarded when destroyed (defaults to POINTS_PER_BRICK)
            hits_required: Number of hits needed to destroy (defaults to 1)
        """
        self.x = float(x)
        self.y = float(y)
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        
        self.color = color if color else (255, 0, 0)  # Default to red
        self.original_color = self.color
        self.points = points if points else POINTS_PER_BRICK
        
        # Durability system
        self.max_hits = hits_required
        self.hits_taken = 0
        self.is_destroyed = False
        
        # Create pygame rect for collision detection - slightly larger to eliminate gaps
        self.rect = pygame.Rect(self.x - 1, self.y - 1, self.width + 2, self.height + 2)
        
        # Visual effects
        self.flash_timer = 0.0
        self.flash_duration = 0.1
    
    def hit(self) -> tuple:
        """Handle brick being hit by ball.
        
        Returns:
            Tuple of (points_awarded, should_drop_powerup)
        """
        if self.is_destroyed:
            return (0, False)
        
        self.hits_taken += 1
        self.flash_timer = self.flash_duration
        
        # Update color based on damage
        self._update_color()
        
        # Check if brick is destroyed
        if self.hits_taken >= self.max_hits:
            self.is_destroyed = True
            # Check if should drop power-up
            should_drop_powerup = random.random() < POWERUP_DROP_CHANCE
            return (self.points, should_drop_powerup)
        
        return (0, False)  # No points until fully destroyed
    
    def _update_color(self):
        """Update brick color based on damage taken."""
        if self.is_destroyed:
            return
        
        # Calculate damage ratio
        damage_ratio = self.hits_taken / self.max_hits
        
        # Darken the color as damage increases
        r, g, b = self.original_color
        factor = 1.0 - (damage_ratio * 0.5)  # Don't go completely dark
        
        self.color = (
            int(r * factor),
            int(g * factor),
            int(b * factor)
        )
    
    def update(self, dt: float):
        """Update brick state (mainly for visual effects).
        
        Args:
            dt: Delta time in seconds
        """
        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= dt
    
    def draw(self, screen: pygame.Surface):
        """Draw the brick on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.is_destroyed:
            return
        
        # Determine color (flash white when hit)
        draw_color = self.color
        if self.flash_timer > 0:
            flash_intensity = self.flash_timer / self.flash_duration
            draw_color = (
                min(255, int(self.color[0] + (255 - self.color[0]) * flash_intensity)),
                min(255, int(self.color[1] + (255 - self.color[1]) * flash_intensity)),
                min(255, int(self.color[2] + (255 - self.color[2]) * flash_intensity))
            )
        
        # Draw main brick
        pygame.draw.rect(screen, draw_color, self.rect)
        
        # Draw border for definition
        border_color = (
            max(0, draw_color[0] - 50),
            max(0, draw_color[1] - 50),
            max(0, draw_color[2] - 50)
        )
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw highlight for 3D effect
        highlight_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, 2)
        highlight_color = (
            min(255, draw_color[0] + 50),
            min(255, draw_color[1] + 50),
            min(255, draw_color[2] + 50)
        )
        pygame.draw.rect(screen, highlight_color, highlight_rect)
        
        # Draw extra border for multi-hit bricks
        if self.max_hits > 1:
            extra_border_color = (255, 255, 255) if self.hits_taken == 0 else (128, 128, 128)
            pygame.draw.rect(screen, extra_border_color, self.rect, 1)
    
    def get_collision_normal(self, ball_pos: tuple) -> tuple:
        """Get collision normal based on ball position.
        
        Args:
            ball_pos: Position of the ball (x, y)
            
        Returns:
            Normal vector (nx, ny) for collision response
        """
        ball_x, ball_y = ball_pos
        brick_center_x = self.x + self.width // 2
        brick_center_y = self.y + self.height // 2
        
        # Calculate relative position
        rel_x = ball_x - brick_center_x
        rel_y = ball_y - brick_center_y
        
        # Determine which side was hit based on relative position
        if abs(rel_x) > abs(rel_y):
            # Hit left or right side
            return (1.0 if rel_x > 0 else -1.0, 0.0)
        else:
            # Hit top or bottom side
            return (0.0, 1.0 if rel_y > 0 else -1.0)


class BrickGrid:
    """Manages a grid of bricks for the game level."""
    
    def __init__(self, rows: int, cols: int, start_x: float, start_y: float, 
                 padding: int = 5):
        """Initialize a grid of bricks.
        
        Args:
            rows: Number of brick rows
            cols: Number of brick columns
            start_x: Starting X position for the grid
            start_y: Starting Y position for the grid
            padding: Padding between bricks
        """
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self.bricks = []
        
        # Create brick grid
        for row in range(rows):
            brick_row = []
            for col in range(cols):
                x = start_x + col * (BRICK_WIDTH + padding)
                y = start_y + row * (BRICK_HEIGHT + padding)
                
                # Get color based on row (from constants)
                color_index = min(row, len(BRICK_COLORS) - 1)
                color = BRICK_COLORS[color_index]
                
                # Create brick with different properties based on row
                # Top rows (0, 1) are harder and worth more points
                if row < 2:
                    hits_required = 2
                    points = POINTS_PER_BRICK * 2
                elif row < 4:
                    hits_required = 2
                    points = POINTS_PER_BRICK * 1.5
                else:
                    hits_required = 1
                    points = POINTS_PER_BRICK
                
                brick = Brick(x, y, color, int(points), hits_required)
                brick_row.append(brick)
            
            self.bricks.append(brick_row)
    
    def update(self, dt: float):
        """Update all bricks in the grid.
        
        Args:
            dt: Delta time in seconds
        """
        for row in self.bricks:
            for brick in row:
                if not brick.is_destroyed:
                    brick.update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw all bricks in the grid.
        
        Args:
            screen: Pygame surface to draw on
        """
        for row in self.bricks:
            for brick in row:
                brick.draw(screen)
    
    def get_active_bricks(self) -> list:
        """Get list of all non-destroyed bricks.
        
        Returns:
            List of active Brick objects
        """
        active_bricks = []
        for row in self.bricks:
            for brick in row:
                if not brick.is_destroyed:
                    active_bricks.append(brick)
        return active_bricks
    
    def is_cleared(self) -> bool:
        """Check if all bricks are destroyed.
        
        Returns:
            True if no active bricks remain
        """
        return len(self.get_active_bricks()) == 0
    
    def get_total_points(self) -> int:
        """Calculate total points available from all bricks.
        
        Returns:
            Total points that can be earned
        """
        total = 0
        for row in self.bricks:
            for brick in row:
                total += brick.points
        return total
