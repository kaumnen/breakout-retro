"""
Main entry point for Breakout game - pygbag compatible.
This is the file that pygbag will use as the entry point.
"""

import asyncio
import pygame
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from breakout.game import Game, GameState
    from breakout.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
    FULL_GAME_AVAILABLE = True
except ImportError as e:
    print(f"Could not import full game: {e}")
    print("Falling back to simple game...")
    FULL_GAME_AVAILABLE = False
    
    # Fallback constants
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)


class SimpleGame:
    """Fallback simple game for testing."""
    
    def __init__(self):
        self.running = True
        self.ball_x = SCREEN_WIDTH // 2
        self.ball_y = SCREEN_HEIGHT // 2
        self.ball_dx = 5
        self.ball_dy = 5
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self, dt):
        """Update game logic."""
        # Simple bouncing ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Bounce off walls
        if self.ball_x <= 10 or self.ball_x >= SCREEN_WIDTH - 10:
            self.ball_dx = -self.ball_dx
        if self.ball_y <= 10 or self.ball_y >= SCREEN_HEIGHT - 10:
            self.ball_dy = -self.ball_dy
    
    def draw(self, screen):
        """Draw the game."""
        screen.fill(BLACK)
        
        # Draw bouncing ball
        pygame.draw.circle(screen, RED, (int(self.ball_x), int(self.ball_y)), 10)
        
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("Breakout Retro (Simple)", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Draw instructions
        font_small = pygame.font.Font(None, 24)
        instruction = font_small.render("ESC to quit", True, WHITE)
        screen.blit(instruction, (10, 10))


async def main():
    """Main game loop - async for pygbag compatibility."""
    print("Starting Breakout Retro...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Retro")
    clock = pygame.time.Clock()
    
    # Try to initialize sound (optional for web)
    try:
        pygame.mixer.init()
    except:
        print("Sound initialization failed - continuing without audio")
    
    # Create game instance
    if FULL_GAME_AVAILABLE:
        print("Using full game implementation...")
        game = Game()
        # Override the screen with our web-compatible one
        game.screen = screen
    else:
        print("Using simple fallback game...")
        game = SimpleGame()
    
    print("Game initialized, starting main loop...")
    
    # Main game loop
    while game.running:
        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0
        
        # Handle events
        if FULL_GAME_AVAILABLE:
            # Let the full game handle its own events
            game.handle_events()
        else:
            # Handle events for simple game
            game.handle_events()
        
        # Update game
        game.update(dt)
        
        # Draw game
        if FULL_GAME_AVAILABLE:
            # Full game draws to its own screen
            game.draw()
        else:
            # Simple game needs screen passed to it
            game.draw(screen)
            pygame.display.flip()
        
        # CRITICAL: Yield control back to browser
        await asyncio.sleep(0)
    
    print("Game ending...")
    pygame.quit()


# Entry point
if __name__ == "__main__":
    asyncio.run(main())
