"""Ball entity for the Breakout game."""

import pygame
import math
import random
from ..utils.constants import (
    BALL_RADIUS, BALL_SPEED, BALL_MAX_SPEED,
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
)
from ..utils.helpers import clamp, normalize_vector


class Ball:
    """Game ball that bounces around the screen."""
    
    def __init__(self, x: float = None, y: float = None):
        """Initialize the ball.
        
        Args:
            x: X position (defaults to center of screen)
            y: Y position (defaults to center of screen)
        """
        self.radius = BALL_RADIUS
        self.speed = BALL_SPEED
        self.max_speed = BALL_MAX_SPEED
        
        # Set default position if not provided
        if x is None:
            x = SCREEN_WIDTH // 2
        if y is None:
            y = SCREEN_HEIGHT // 2
            
        self.x = float(x)
        self.y = float(y)
        
        # Initialize velocity with random angle upward
        self.reset_velocity()
        
        # Create pygame rect for collision detection
        self.rect = pygame.Rect(
            self.x - self.radius, 
            self.y - self.radius, 
            self.radius * 2, 
            self.radius * 2
        )
        
        # Trail effect (optional visual enhancement)
        self.trail_positions = []
        self.max_trail_length = 5
    
    def reset_velocity(self, angle: float = None):
        """Reset ball velocity with specified or random angle.
        
        Args:
            angle: Angle in radians (defaults to random upward angle)
        """
        if angle is None:
            # Random angle between 45 and 135 degrees (upward)
            angle = math.radians(random.uniform(45, 135))
        
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = -math.sin(angle) * self.speed  # Negative for upward movement
    
    def update(self, dt: float):
        """Update ball position and handle wall collisions.
        
        Args:
            dt: Delta time in seconds
        """
        # Store previous position for trail effect
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        
        # Store previous position for collision detection
        prev_x, prev_y = self.x, self.y
        
        # Update position
        movement_scale = dt * 60  # Scale by 60 for consistent movement
        self.x += self.velocity_x * movement_scale
        self.y += self.velocity_y * movement_scale
        
        # Handle wall collisions
        self._handle_wall_collisions()
        
        # Update rect position
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)
        
        # Clamp speed to maximum
        current_speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.velocity_x *= scale
            self.velocity_y *= scale
    
    def _handle_wall_collisions(self):
        """Handle collisions with screen boundaries."""
        # Left and right walls
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.velocity_x = abs(self.velocity_x)  # Bounce right
        elif self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.velocity_x = -abs(self.velocity_x)  # Bounce left
        
        # Top wall
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.velocity_y = abs(self.velocity_y)  # Bounce down
        
        # Bottom wall is handled by game logic (lose life)
    
    def bounce_off_paddle(self, paddle_collision_factor: float):
        """Bounce off paddle with angle based on hit position.
        
        Args:
            paddle_collision_factor: Factor from -1.0 to 1.0 indicating hit position
        """
        # Calculate new angle based on paddle hit position
        max_angle = math.radians(75)  # Maximum bounce angle
        angle = paddle_collision_factor * max_angle
        
        # Ensure ball always goes upward
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        self.velocity_x = math.sin(angle) * speed
        self.velocity_y = -abs(math.cos(angle) * speed)  # Always negative (upward)
        
        # Slightly increase speed on paddle hit
        speed_increase = 1.02
        self.velocity_x *= speed_increase
        self.velocity_y *= speed_increase
    
    def bounce_off_brick(self, collision_normal: tuple, brick_rect: pygame.Rect = None):
        """Bounce off brick using collision normal.
        
        Args:
            collision_normal: Normal vector (nx, ny) of the collision surface
            brick_rect: Rectangle of the brick (for position correction)
        """
        # Ensure we have a valid normal
        nx, ny = collision_normal
        if nx == 0 and ny == 0:
            return  # Invalid normal, skip collision
        
        # Calculate dot product for reflection
        dot_product = self.velocity_x * nx + self.velocity_y * ny
        
        # Only reflect if moving towards the surface
        if dot_product < 0:
            # Reflect velocity vector off the surface
            self.velocity_x -= 2 * dot_product * nx
            self.velocity_y -= 2 * dot_product * ny
            
            # Position correction to prevent ball from getting stuck inside brick
            if brick_rect:
                # Move ball outside the brick based on collision normal
                separation_distance = self.radius + 2  # Extra buffer
                self.x += nx * separation_distance
                self.y += ny * separation_distance
                
                # Ensure ball doesn't go outside screen bounds
                self.x = clamp(self.x, self.radius, SCREEN_WIDTH - self.radius)
                self.y = clamp(self.y, self.radius, SCREEN_HEIGHT - self.radius)
    
    def draw(self, screen: pygame.Surface):
        """Draw the ball and its trail on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw trail effect
        for i, pos in enumerate(self.trail_positions):
            alpha = (i + 1) / len(self.trail_positions)
            trail_radius = int(self.radius * alpha * 0.7)
            if trail_radius > 0:
                trail_color = (int(WHITE[0] * alpha), int(WHITE[1] * alpha), int(WHITE[2] * alpha))
                pygame.draw.circle(screen, trail_color, (int(pos[0]), int(pos[1])), trail_radius)
        
        # Draw main ball
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        
        # Add a subtle highlight for 3D effect
        highlight_offset = self.radius // 3
        highlight_pos = (int(self.x - highlight_offset), int(self.y - highlight_offset))
        pygame.draw.circle(screen, (255, 255, 255), highlight_pos, self.radius // 4)
    
    def get_position(self) -> tuple:
        """Get the current position of the ball.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
    
    def get_velocity(self) -> tuple:
        """Get the current velocity of the ball.
        
        Returns:
            Tuple of (vx, vy) velocity components
        """
        return (self.velocity_x, self.velocity_y)
    
    def set_position(self, x: float, y: float):
        """Set the ball position.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = float(x)
        self.y = float(y)
        self.trail_positions.clear()  # Clear trail when repositioning
    
    def is_below_screen(self) -> bool:
        """Check if ball has fallen below the screen.
        
        Returns:
            True if ball is below screen bottom
        """
        return self.y - self.radius > SCREEN_HEIGHT
