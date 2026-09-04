"""Core game logic and state management."""

import asyncio
import math
import random
from enum import Enum

import pygame

from .entities import Paddle, Ball, PowerUp
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
        self.font_title = pygame.font.Font(None, 76)
        self.font_large = pygame.font.Font(None, 52)
        self.font_medium = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 22)
        self.font_tiny = pygame.font.Font(None, 18)
        self.background = self._create_background()
        
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
        
        # Power-up feedback
        self.powerup_message = ""
        self.powerup_message_timer = 0
        self.slow_ball_timer = 0.0
        
        # Input handling
        self.keys_pressed = {}
        self.mouse_pos = None
        
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
        self.powerup_message = ""
        self.powerup_message_timer = 0
        self.slow_ball_timer = 0.0
        self.keys_pressed.clear()

    def _create_background(self) -> pygame.Surface:
        """Create the static gradient, stars, and perspective grid."""
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = tuple(
                int(top + (bottom - top) * ratio)
                for top, bottom in zip(BACKGROUND_TOP, BACKGROUND_BOTTOM)
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

        rng = random.Random(1986)
        for _ in range(70):
            x = rng.randrange(SCREEN_WIDTH)
            y = rng.randrange(48, SCREEN_HEIGHT - 90)
            shade = rng.choice([(36, 48, 88), (43, 61, 103), (56, 53, 105)])
            surface.set_at((x, y), shade)

        horizon = SCREEN_HEIGHT - 105
        grid_color = (31, 34, 78)
        pygame.draw.line(surface, (52, 42, 103), (0, horizon), (SCREEN_WIDTH, horizon), 2)
        for x in range(-200, SCREEN_WIDTH + 201, 80):
            pygame.draw.line(surface, grid_color, (SCREEN_WIDTH // 2, horizon), (x, SCREEN_HEIGHT))
        for y in range(horizon + 20, SCREEN_HEIGHT, 20):
            pygame.draw.line(surface, grid_color, (0, y), (SCREEN_WIDTH, y))
        return surface

    def start_game(self):
        """Start a fresh run from any non-playing state."""
        self.reset_game()
        self.state = GameState.PLAYING
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                
                # State-specific key handling
                if self.state == GameState.MENU:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_game()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_SPACE:
                        if self.paddle.stuck_ball:
                            self.paddle.release_stuck_ball()
                        else:
                            self.paddle.fire_laser()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_r:
                        self.start_game()
                
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.reset_game()
                        self.state = GameState.MENU
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_pos = event.pos
                if self.state == GameState.MENU:
                    self.start_game()
                elif self.state == GameState.PLAYING:
                    if self.paddle.stuck_ball:
                        self.paddle.release_stuck_ball()
                    else:
                        self.paddle.fire_laser()

            elif event.type == pygame.WINDOWFOCUSLOST:
                if self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
    
    def update(self, dt: float):
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state != GameState.PLAYING:
            return

        # Avoid tunnelling and giant timer jumps when a browser tab wakes up.
        dt = min(max(dt, 0.0), 1 / 30)
        
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

        if self.slow_ball_timer > 0:
            self.slow_ball_timer = max(0.0, self.slow_ball_timer - dt)
            if self.slow_ball_timer == 0:
                for ball in self.balls:
                    ball.set_slowed(False)
        
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
        # Check collisions for each ball
        for ball in self.balls:
            ball_pos = ball.get_position()
            
            # Ball-paddle collision
            if circle_rect_collision(ball_pos, ball.radius, self.paddle.rect):
                # Only bounce if the ball is approaching the paddle.
                if ball.velocity_y > 0:
                    ball.y = self.paddle.rect.top - ball.radius - 1
                    # Check for sticky paddle
                    if self.paddle.is_sticky and not self.paddle.stuck_ball:
                        self.paddle.stick_ball(ball)
                    else:
                        collision_factor = self.paddle.get_collision_factor(ball_pos[0])
                        ball.bounce_off_paddle(collision_factor)
            
            # Resolve at most one brick per ball, independently. A global
            # cooldown made extra balls pass through bricks after another hit.
            active_bricks = self.brick_grid.get_active_bricks()
            colliding_bricks = [
                brick for brick in active_bricks
                if circle_rect_collision(ball_pos, ball.radius, brick.rect)
            ]
            if colliding_bricks:
                closest_brick = min(
                    colliding_bricks,
                    key=lambda brick: (
                        (ball_pos[0] - brick.rect.centerx) ** 2
                        + (ball_pos[1] - brick.rect.centery) ** 2
                    ),
                )
                collision_normal = get_collision_normal(
                    ball.get_previous_position(), closest_brick.rect
                )
                ball.bounce_off_brick(collision_normal, closest_brick.rect)
                points, should_drop_powerup = closest_brick.hit()
                self.score += points

                if should_drop_powerup:
                    self.powerups.append(PowerUp(*closest_brick.rect.center))
        
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
                    angle = random.uniform(30, 150)
                    new_ball.reset_velocity(math.radians(angle))
                    if self.slow_ball_timer > 0:
                        new_ball.set_slowed(True)
                    self.balls.append(new_ball)
        
        elif powerup.type == POWERUP_EXTRA_LIFE:
            self.lives += 1
        
        elif powerup.type == POWERUP_SLOW_BALL:
            self.slow_ball_timer = POWERUP_DURATION
            for ball in self.balls:
                ball.set_slowed(True)
        
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
        if self.brick_grid.is_cleared():
            self.state = GameState.VICTORY
            return

        # Check if all balls fell below screen
        if not self.balls:
            self.lives -= 1
            
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                # Begin a clean serve without carrying transient effects over.
                self.paddle = Paddle()
                self.powerups.clear()
                self.slow_ball_timer = 0.0
                new_ball = Ball()
                paddle_center = self.paddle.get_top_center()
                new_ball.set_position(paddle_center[0], paddle_center[1] - 50)
                self.balls = [new_ball]
                self.ball = new_ball
    
    def draw(self):
        """Render the game."""
        self.screen.blit(self.background, (0, 0))
        
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
        # A compact brick mark makes the menu feel related to the playfield.
        logo_colors = [RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE]
        for index, color in enumerate(logo_colors):
            rect = pygame.Rect(263 + index * 46, 112, 40, 8)
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

        shadow = self.font_title.render("BREAKOUT", True, (31, 45, 91))
        title = self.font_title.render("BREAKOUT", True, WHITE)
        self.screen.blit(shadow, shadow.get_rect(center=(404, 178)))
        self.screen.blit(title, title.get_rect(center=(400, 174)))

        subtitle = self.font_medium.render("R E T R O   R E M I X", True, ACCENT)
        self.screen.blit(subtitle, subtitle.get_rect(center=(400, 224)))

        panel = pygame.Rect(214, 282, 372, 198)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=14)
        pygame.draw.rect(self.screen, PANEL_BORDER, panel, 2, border_radius=14)

        start_text = self.font_medium.render("SPACE / CLICK TO PLAY", True, YELLOW)
        self.screen.blit(start_text, start_text.get_rect(center=(400, 323)))
        pygame.draw.line(self.screen, PANEL_BORDER, (250, 348), (550, 348), 1)

        controls = [
            ("MOVE", "mouse  /  arrows  /  A D"),
            ("ACTION", "space or click"),
            ("PAUSE", "escape"),
        ]
        for row, (label, value) in enumerate(controls):
            y = 374 + row * 31
            label_surface = self.font_tiny.render(label, True, MUTED_TEXT)
            value_surface = self.font_small.render(value, True, WHITE)
            self.screen.blit(label_surface, (260, y + 3))
            self.screen.blit(value_surface, (352, y))

        footer = self.font_tiny.render(
            "CLEAR THE WALL  •  CATCH POWER-UPS  •  KEEP THE BALL ALIVE",
            True,
            MUTED_TEXT,
        )
        self.screen.blit(footer, footer.get_rect(center=(400, 536)))
    
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
        hud = pygame.Rect(10, 9, SCREEN_WIDTH - 20, 43)
        pygame.draw.rect(self.screen, PANEL, hud, border_radius=9)
        pygame.draw.rect(self.screen, PANEL_BORDER, hud, 1, border_radius=9)

        score_label = self.font_tiny.render("SCORE", True, MUTED_TEXT)
        score_value = self.font_medium.render(f"{self.score:06d}", True, WHITE)
        self.screen.blit(score_label, (25, 17))
        self.screen.blit(score_value, (82, 13))

        lives_label = self.font_tiny.render("LIVES", True, MUTED_TEXT)
        self.screen.blit(lives_label, (326, 17))
        visible_lives = min(self.lives, 5)
        for index in range(visible_lives):
            center = (385 + index * 18, 30)
            pygame.draw.circle(self.screen, (92, 31, 59), center, 6)
            pygame.draw.circle(self.screen, RED, center, 4)
        if self.lives > visible_lives:
            extra_lives = self.font_tiny.render(f"+{self.lives - visible_lives}", True, RED)
            self.screen.blit(extra_lives, (475, 22))

        level_label = self.font_tiny.render("STAGE", True, MUTED_TEXT)
        level_value = self.font_medium.render(f"{self.level:02d}", True, CYAN)
        self.screen.blit(level_label, (682, 17))
        self.screen.blit(level_value, (746, 13))

        self.draw_powerup_timers()
        
        # Power-up message
        if self.powerup_message:
            message_text = self.font_large.render(self.powerup_message, True, YELLOW)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 315))
            
            # Draw background for message
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, PANEL, bg_rect, border_radius=8)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 2, border_radius=8)
            
            self.screen.blit(message_text, message_rect)
    
    def draw_powerup_timers(self):
        """Draw active power-up timers."""
        effects = list(self.paddle.active_powerups.items())
        if self.slow_ball_timer > 0:
            effects.append((POWERUP_SLOW_BALL, self.slow_ball_timer))

        if not effects:
            return

        names = {
            POWERUP_LARGE_PADDLE: "WIDE",
            POWERUP_SMALL_PADDLE: "SMALL",
            POWERUP_LASER_PADDLE: "LASER",
            POWERUP_STICKY_PADDLE: "STICKY",
            POWERUP_SLOW_BALL: "SLOW",
        }
        x = SCREEN_WIDTH - 186
        y = 252
        for powerup_type, remaining_time in effects:
            panel = pygame.Rect(x, y, 166, 31)
            pygame.draw.rect(self.screen, PANEL, panel, border_radius=7)
            pygame.draw.rect(self.screen, PANEL_BORDER, panel, 1, border_radius=7)

            suffix = (
                f" {self.paddle.laser_shots_remaining}×"
                if powerup_type == POWERUP_LASER_PADDLE
                else ""
            )
            label = self.font_tiny.render(
                f"{names.get(powerup_type, powerup_type.upper())}{suffix}", True, WHITE
            )
            self.screen.blit(label, (x + 9, y + 7))

            progress = max(0.0, min(1.0, remaining_time / POWERUP_DURATION))
            pygame.draw.rect(self.screen, (38, 47, 78), (x + 92, y + 13, 63, 5), border_radius=3)
            pygame.draw.rect(
                self.screen,
                POWERUP_COLORS.get(powerup_type, ACCENT),
                (x + 92, y + 13, int(63 * progress), 5),
                border_radius=3,
            )
            y += 37
    
    def draw_pause_overlay(self):
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(185)
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
        overlay.set_alpha(195)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_medium.render("SPACE / R - RESTART   •   ESC - MENU", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """Draw victory screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(195)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        victory_text = self.font_large.render("VICTORY!", True, GREEN)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, victory_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font_medium.render("SPACE / R - RESTART   •   ESC - MENU", True, WHITE)
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
