"""Helper functions and utilities."""

import pygame
import math
from typing import Tuple


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max values."""
    return max(min_value, min(value, max_value))


def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate distance between two points."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize a 2D vector."""
    magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude == 0:
        return (0, 0)
    return (vector[0] / magnitude, vector[1] / magnitude)


def reflect_vector(vector: Tuple[float, float], normal: Tuple[float, float]) -> Tuple[float, float]:
    """Reflect a vector off a surface with given normal."""
    dot_product = vector[0] * normal[0] + vector[1] * normal[1]
    return (
        vector[0] - 2 * dot_product * normal[0],
        vector[1] - 2 * dot_product * normal[1]
    )


def circle_rect_collision(circle_pos: Tuple[float, float], radius: float, 
                         rect: pygame.Rect) -> bool:
    """Check collision between circle and rectangle with improved corner detection."""
    cx, cy = circle_pos
    
    # Find the closest point on the rectangle to the circle center
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    
    # Calculate distance from circle center to closest point
    distance_x = cx - closest_x
    distance_y = cy - closest_y
    distance_squared = distance_x * distance_x + distance_y * distance_y
    
    return distance_squared <= (radius * radius)


def get_collision_normal(circle_pos: Tuple[float, float], rect: pygame.Rect) -> Tuple[float, float]:
    """Get the normal vector for collision between circle and rectangle."""
    cx, cy = circle_pos
    
    # Find the closest point on the rectangle
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    
    # Calculate the vector from closest point to circle center
    dx = cx - closest_x
    dy = cy - closest_y
    
    # If the closest point is inside the rectangle (shouldn't happen with proper collision)
    if dx == 0 and dy == 0:
        # Default to vertical collision
        if cy < rect.centery:
            return (0.0, -1.0)  # Top
        else:
            return (0.0, 1.0)   # Bottom
    
    # Normalize the vector to get the collision normal
    length = math.sqrt(dx * dx + dy * dy)
    if length == 0:
        return (0.0, -1.0)  # Default normal
    
    return (dx / length, dy / length)


def create_text_surface(text: str, font: pygame.font.Font, color: Tuple[int, int, int]) -> pygame.Surface:
    """Create a text surface with the given font and color."""
    return font.render(text, True, color)
