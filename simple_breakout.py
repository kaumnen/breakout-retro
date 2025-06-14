"""Simple standalone Breakout game for pygbag testing."""

import asyncio
import pygame
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game settings
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 8
BALL_RADIUS = 8
BALL_SPEED = 5
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_ROWS = 6
BRICK_COLS = 10

class SimpleBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = BALL_SPEED
        self.dy = -BALL_SPEED
        self.radius = BALL_RADIUS
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
        # Bounce off walls
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.dx = -self.dx
        if self.y <= self.radius:
            self.dy = -self.dy
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

class SimplePaddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
    
    def update(self, mouse_x):
        self.x = mouse_x - self.width // 2
        # Keep paddle on screen
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class SimpleBrick:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.color = color
        self.alive = True
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

async def main():
    """Simple Breakout game."""
    print("Starting Simple Breakout...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Breakout")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # Game state
    game_state = "menu"  # menu, playing, game_over
    score = 0
    lives = 3
    
    # Create game objects
    ball = SimpleBall(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    paddle = SimplePaddle()
    
    # Create bricks
    bricks = []
    colors = [RED, ORANGE, YELLOW, GREEN, BLUE, (128, 0, 128)]  # Purple
    brick_start_x = (SCREEN_WIDTH - (BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * 5)) // 2
    
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = brick_start_x + col * (BRICK_WIDTH + 5)
            y = 60 + row * (BRICK_HEIGHT + 5)
            color = colors[row % len(colors)]
            bricks.append(SimpleBrick(x, y, color))
    
    print("Game initialized, entering main loop...")
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "menu":
                        game_state = "playing"
                        print("Starting game...")
                    elif game_state == "game_over":
                        # Reset game
                        game_state = "playing"
                        score = 0
                        lives = 3
                        ball = SimpleBall(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        # Reset bricks
                        for brick in bricks:
                            brick.alive = True
                elif event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        game_state = "menu"
        
        # Update game
        if game_state == "playing":
            # Get mouse position for paddle
            mouse_x = pygame.mouse.get_pos()[0]
            paddle.update(mouse_x)
            
            # Update ball
            ball.update()
            
            # Ball-paddle collision
            if (ball.y + ball.radius >= paddle.y and 
                ball.x >= paddle.x and ball.x <= paddle.x + paddle.width and
                ball.dy > 0):
                ball.dy = -ball.dy
                # Add some angle based on where ball hits paddle
                hit_pos = (ball.x - paddle.x) / paddle.width
                ball.dx = BALL_SPEED * (hit_pos - 0.5) * 2
            
            # Ball-brick collisions
            ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, 
                                  ball.radius * 2, ball.radius * 2)
            for brick in bricks:
                if brick.alive and ball_rect.colliderect(brick.get_rect()):
                    brick.alive = False
                    ball.dy = -ball.dy
                    score += 10
                    break
            
            # Check if ball fell off screen
            if ball.y > SCREEN_HEIGHT:
                lives -= 1
                if lives <= 0:
                    game_state = "game_over"
                else:
                    ball = SimpleBall(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            
            # Check if all bricks destroyed
            if all(not brick.alive for brick in bricks):
                game_state = "game_over"  # Could be "victory" state
        
        # Draw everything
        screen.fill(BLACK)
        
        if game_state == "menu":
            title_text = font.render("SIMPLE BREAKOUT", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(title_text, title_rect)
            
            start_text = font.render("Press SPACE to start", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(start_text, start_rect)
        
        elif game_state == "playing":
            # Draw game objects
            ball.draw(screen)
            paddle.draw(screen)
            for brick in bricks:
                brick.draw(screen)
            
            # Draw UI
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            lives_text = font.render(f"Lives: {lives}", True, WHITE)
            screen.blit(lives_text, (10, 50))
        
        elif game_state == "game_over":
            game_over_text = font.render("GAME OVER", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(final_score_text, final_score_rect)
            
            restart_text = font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)
    
    print("Game ended")
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
