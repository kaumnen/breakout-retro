"""Core game logic and state management."""

import asyncio
import pygame
import math
from enum import Enum
from .entities import Paddle, Ball, Brick, PowerUp
from .entities.brick import BrickGrid
from .utils.constants import *
from .utils.helpers import circle_rect_collision, get_collision_normal


class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"


class Game:
    """Main game class that manages all game logic and rendering."""
    
    def __init__(self):
        """Initialize the game."""
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Breakout Retro")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        
        # Game objects
        self.paddle = None
        self.ball = None
        self.balls = []  # For multi-ball power-up
        self.brick_grid = None
        self.powerups = []  # Active power-ups
        
        # Game statistics
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        
        # Collision handling
        self.last_collision_time = 0
        self.collision_cooldown = 0.1  # Increased from 0.05 to 0.1 seconds
        
        # Power-up feedback
        self.powerup_message = ""
        self.powerup_message_timer = 0
        
        # Input handling
        self.keys_pressed = {}
        self.mouse_pos = (0, 0)
        
        # Initialize game objects
        self.reset_game()
    
    def reset_game(self):
        """Reset game to initial state."""
        # Create game objects
        self.paddle = Paddle()
        self.ball = Ball()
        self.balls = [self.ball]  # Start with one ball
        self.powerups = []
        
        # Position ball above paddle
        paddle_center = self.paddle.get_top_center()
        self.ball.set_position(paddle_center[0], paddle_center[1] - 50)
        
        # Create brick grid
        grid_start_x = (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING) - BRICK_PADDING)) // 2
        self.brick_grid = BrickGrid(
            BRICK_ROWS, BRICK_COLS, 
            grid_start_x, BRICK_Y_OFFSET, 
            BRICK_PADDING
        )
        
        # Reset stats
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                
                # State-specific key handling
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
    
    def update(self, dt: float):
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state != GameState.PLAYING:
            return
        
        # Update game objects
        self.paddle.handle_input(self.keys_pressed, self.mouse_pos)
        self.paddle.update(dt)
        
        # Update all balls
        for ball in self.balls[:]:  # Use slice to avoid modification during iteration
            ball.update(dt)
            
            # Remove balls that fell below screen
            if ball.is_below_screen():
                self.balls.remove(ball)
        
        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if powerup.is_below_screen():
                self.powerups.remove(powerup)
        
        self.brick_grid.update(dt)
        
        # Check collisions
        self.check_collisions()
        
        # Update power-up message timer
        if self.powerup_message_timer > 0:
            self.powerup_message_timer -= dt
            if self.powerup_message_timer <= 0:
                self.powerup_message = ""
        
        # Check game conditions
        self.check_game_conditions()
    
    def check_collisions(self):
        """Check and handle all collision detection."""
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Check collisions for each ball
        for ball in self.balls:
            ball_pos = ball.get_position()
            
            # Ball-paddle collision
            if circle_rect_collision(ball_pos, ball.radius, self.paddle.rect):
                # Only bounce if ball is moving downward and enough time has passed
                if ball.velocity_y > 0 and (current_time - self.last_collision_time) > self.collision_cooldown:
                    # Check for sticky paddle
                    if self.paddle.is_sticky and not self.paddle.stuck_ball:
                        self.paddle.stick_ball(ball)
                    else:
                        collision_factor = self.paddle.get_collision_factor(ball_pos[0])
                        ball.bounce_off_paddle(collision_factor)
                    self.last_collision_time = current_time
            
            # Ball-brick collisions - only if enough time has passed since last collision
            if (current_time - self.last_collision_time) > self.collision_cooldown:
                active_bricks = self.brick_grid.get_active_bricks()
                closest_brick = None
                closest_distance = float('inf')
                
                for brick in active_bricks:
                    if circle_rect_collision(ball_pos, ball.radius, brick.rect):
                        # Calculate distance from ball to brick center
                        brick_center = (brick.x + brick.width // 2, brick.y + brick.height // 2)
                        distance = ((ball_pos[0] - brick_center[0])**2 + (ball_pos[1] - brick_center[1])**2)**0.5
                        
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_brick = brick
                
                # Handle collision with closest brick only
                if closest_brick:
                    collision_normal = get_collision_normal(ball_pos, closest_brick.rect)
                    ball.bounce_off_brick(collision_normal, closest_brick.rect)
                    
                    # Hit the brick and add score
                    points, should_drop_powerup = closest_brick.hit()
                    self.score += points
                    
                    # Drop power-up if needed
                    if should_drop_powerup:
                        powerup_x = closest_brick.x + closest_brick.width // 2
                        powerup_y = closest_brick.y + closest_brick.height // 2
                        powerup = PowerUp(powerup_x, powerup_y)
                        self.powerups.append(powerup)
                    
                    # Update collision time
                    self.last_collision_time = current_time
                    break  # Only one brick collision per ball per frame
        
        # Power-up collection
        for powerup in self.powerups[:]:
            if not powerup.collected:
                # Use more generous collision detection for power-up collection
                powerup_rect = pygame.Rect(
                    powerup.x - powerup.size // 2,
                    powerup.y - powerup.size // 2,
                    powerup.size,
                    powerup.size
                )
                
                if self.paddle.rect.colliderect(powerup_rect):
                    self.collect_powerup(powerup)
                    powerup.collect()
                    self.powerups.remove(powerup)
        
        # Laser-brick collisions
        for laser in self.paddle.get_lasers():
            if not laser.active:
                continue
                
            active_bricks = self.brick_grid.get_active_bricks()
            for brick in active_bricks:
                if laser.get_rect().colliderect(brick.rect):
                    # Hit the brick
                    points, should_drop_powerup = brick.hit()
                    self.score += points
                    
                    # Drop power-up if needed
                    if should_drop_powerup:
                        powerup_x = brick.x + brick.width // 2
                        powerup_y = brick.y + brick.height // 2
                        powerup = PowerUp(powerup_x, powerup_y)
                        self.powerups.append(powerup)
                    
                    # Deactivate laser
                    laser.active = False
                    break  # One brick per laser
    
    def collect_powerup(self, powerup: PowerUp):
        """Handle power-up collection.
        
        Args:
            powerup: The collected power-up
        """
        from .utils.constants import (
            POWERUP_MULTIBALL, POWERUP_EXTRA_LIFE, POWERUP_SLOW_BALL,
            POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE, 
            POWERUP_LASER_PADDLE, POWERUP_STICKY_PADDLE
        )
        
        if powerup.type == POWERUP_MULTIBALL:
            # Create additional balls
            if self.balls:  # Make sure we have at least one ball to copy from
                main_ball = self.balls[0]
                for i in range(2):  # Add 2 more balls
                    new_ball = Ball(main_ball.x, main_ball.y)
                    # Give them different angles
                    import random
                    angle = random.uniform(30, 150)
                    new_ball.reset_velocity(math.radians(angle))
                    self.balls.append(new_ball)
        
        elif powerup.type == POWERUP_EXTRA_LIFE:
            self.lives += 1
        
        elif powerup.type == POWERUP_SLOW_BALL:
            # Slow down all balls
            for ball in self.balls:
                ball.velocity_x *= 0.7
                ball.velocity_y *= 0.7
        
        elif powerup.type in [POWERUP_LARGE_PADDLE, POWERUP_SMALL_PADDLE, 
                             POWERUP_LASER_PADDLE, POWERUP_STICKY_PADDLE]:
            self.paddle.apply_powerup(powerup.type)
        
        # Show collection message
        powerup_names = {
            POWERUP_MULTIBALL: "MULTI-BALL!",
            POWERUP_EXTRA_LIFE: "EXTRA LIFE!",
            POWERUP_SLOW_BALL: "SLOW BALL!",
            POWERUP_LARGE_PADDLE: "LARGE PADDLE!",
            POWERUP_SMALL_PADDLE: "SMALL PADDLE!",
            POWERUP_LASER_PADDLE: "LASER PADDLE!",
            POWERUP_STICKY_PADDLE: "STICKY PADDLE!"
        }
        
        self.powerup_message = powerup_names.get(powerup.type, "POWER-UP!")
        self.powerup_message_timer = 2.0  # Show for 2 seconds
    
    def check_game_conditions(self):
        """Check for game over, victory, or life loss conditions."""
        # Check if all balls fell below screen
        if not self.balls:
            self.lives -= 1
            
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                # Reset with one ball
                new_ball = Ball()
                paddle_center = self.paddle.get_top_center()
                new_ball.set_position(paddle_center[0], paddle_center[1] - 50)
                self.balls = [new_ball]
                # Keep reference to main ball for compatibility
                self.ball = new_ball
        
        # Check for victory (all bricks destroyed)
        if self.brick_grid.is_cleared():
            self.state = GameState.VICTORY
    
    def draw(self):
        """Render the game."""
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_game()
            self.draw_victory()
        
        # Update display
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw the main menu."""
        title_text = self.font_large.render("BREAKOUT RETRO", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)
        
        start_text = self.font_medium.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(start_text, start_rect)
        
        controls_text = [
            "Controls:",
            "Arrow Keys or A/D - Move Paddle",
            "Mouse - Follow Mouse Position",
            "ESC - Pause Game"
        ]
        
        y_offset = SCREEN_HEIGHT // 2 + 80
        for line in controls_text:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
    
    def draw_game(self):
        """Draw the main game screen."""
        # Draw game objects
        self.brick_grid.draw(self.screen)
        self.paddle.draw(self.screen)
        
        # Draw all balls
        for ball in self.balls:
            ball.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw game UI elements."""
        # Score - top left
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives - bottom left to avoid brick overlap
        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, WHITE)
        lives_rect = lives_text.get_rect(bottomleft=(10, SCREEN_HEIGHT - 10))
        self.screen.blit(lives_text, lives_rect)
        
        # Level - bottom right
        level_text = self.font_medium.render(f"Level: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        self.screen.blit(level_text, level_rect)
        
        # Power-up message
        if self.powerup_message:
            message_text = self.font_large.render(self.powerup_message, True, (255, 255, 0))
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            
            # Draw background for message
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 0), bg_rect, 2)
            
            self.screen.blit(message_text, message_rect)
    
    def draw_powerup_timers(self):
        """Draw active power-up timers."""
        if not self.paddle.active_powerups:
            return
        
        y_offset = 150  # Start below power-up message
        
        for powerup_type, remaining_time in self.paddle.active_powerups.items():
            # Power-up names for display
            powerup_names = {
                POWERUP_LARGE_PADDLE: "Large Paddle",
                POWERUP_SMALL_PADDLE: "Small Paddle",
                POWERUP_LASER_PADDLE: "Laser Paddle",
                POWERUP_STICKY_PADDLE: "Sticky Paddle"
            }
            
            name = powerup_names.get(powerup_type, powerup_type)
            
            # Special handling for laser paddle
            if powerup_type == POWERUP_LASER_PADDLE:
                text = f"{name}: {self.paddle.laser_shots_remaining} shots ({remaining_time:.1f}s)"
            else:
                text = f"{name}: {remaining_time:.1f}s"
            
            # Draw timer text
            timer_text = self.font_small.render(text, True, WHITE)
            timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            
            # Draw background
            bg_rect = timer_rect.inflate(10, 4)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
            
            # Draw progress bar
            progress = remaining_time / POWERUP_DURATION
            bar_width = 100
            bar_height = 4
            bar_x = timer_rect.centerx - bar_width // 2
            bar_y = timer_rect.bottom + 5
            
            # Background bar
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress_width = int(bar_width * progress)
            if progress > 0.3:
                color = (0, 255, 0)  # Green
            elif progress > 0.1:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
            
            pygame.draw.rect(self.screen, color, 
                           (bar_x, bar_y, progress_width, bar_height))
            
            self.screen.blit(timer_text, timer_rect)
            y_offset += 35
        
        # Power-up timers
        self.draw_powerup_timers()
    
    def draw_pause_overlay(self):
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font_medium.render("ESC - Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(resume_text, resume_rect)
        
        restart_text = self.font_medium.render("R - Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_game_over(self):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_medium.render("R - Restart | ESC - Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """Draw victory screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_text = self.font_large.render("VICTORY!", True, GREEN)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, victory_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_medium.render("R - Restart | ESC - Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    async def run(self):
        """Main game loop with WebAssembly compatibility."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update game logic
            self.update(dt)
            
            # Render
            self.draw()
            
            # Yield control for WebAssembly
            await asyncio.sleep(0)
