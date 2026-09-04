"""Regression tests for core Breakout gameplay."""

import os
import sys
import unittest
from pathlib import Path


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pygame

from breakout.entities import Ball, PowerUp
from breakout.game import Game, GameState
from breakout.utils.constants import (
    INITIAL_LIVES,
    POWERUP_LARGE_PADDLE,
    POWERUP_LASER_PADDLE,
    POWERUP_SLOW_BALL,
    POWERUP_SMALL_PADDLE,
)
from breakout.utils.helpers import get_collision_normal


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        pygame.event.clear()
        self.game = Game()

    def test_starting_from_menu_always_resets_the_run(self):
        self.game.state = GameState.MENU
        self.game.score = 999
        self.game.lives = 0

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.game.handle_events()

        self.assertEqual(self.game.state, GameState.PLAYING)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, INITIAL_LIVES)
        self.assertEqual(len(self.game.balls), 1)

    def test_space_fires_laser_and_respects_cooldown(self):
        self.game.state = GameState.PLAYING
        self.game.paddle.apply_powerup(POWERUP_LASER_PADDLE)

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.game.handle_events()
        self.assertEqual(len(self.game.paddle.lasers), 2)
        self.assertEqual(self.game.paddle.laser_shots_remaining, 19)

        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.game.handle_events()
        self.assertEqual(len(self.game.paddle.lasers), 2)

    def test_slow_ball_expires_without_changing_velocity(self):
        ball = self.game.balls[0]
        original_velocity = ball.get_velocity()
        self.game.collect_powerup(PowerUp(0, 0, POWERUP_SLOW_BALL))
        self.assertEqual(ball.slow_multiplier, 0.7)

        self.game.state = GameState.PLAYING
        self.game.slow_ball_timer = 0.01
        self.game.update(0.02)

        self.assertEqual(ball.slow_multiplier, 1.0)
        self.assertEqual(ball.get_velocity(), original_velocity)

    def test_each_ball_can_hit_a_different_brick_in_one_frame(self):
        first = self.game.brick_grid.bricks[0][0]
        second = self.game.brick_grid.bricks[0][2]
        balls = []
        for brick in (first, second):
            ball = Ball(*brick.rect.center)
            ball.velocity_x = 0
            ball.velocity_y = 6
            ball.set_position(*brick.rect.center)
            balls.append(ball)
        self.game.balls = balls

        self.game.check_collisions()

        self.assertEqual(first.hits_taken, 1)
        self.assertEqual(second.hits_taken, 1)

    def test_paddle_size_powerups_are_mutually_exclusive(self):
        original_width = self.game.paddle.width
        self.game.paddle.apply_powerup(POWERUP_LARGE_PADDLE)
        self.assertGreater(self.game.paddle.width, original_width)

        self.game.paddle.apply_powerup(POWERUP_SMALL_PADDLE)
        self.assertLess(self.game.paddle.width, original_width)
        self.assertNotIn(POWERUP_LARGE_PADDLE, self.game.paddle.active_powerups)

    def test_active_effect_hud_renders_without_recursion(self):
        self.game.paddle.apply_powerup(POWERUP_LASER_PADDLE)
        self.game.draw_powerup_timers()

    def test_collision_normal_uses_nearest_edge_when_center_is_inside(self):
        rect = pygame.Rect(100, 100, 80, 20)
        self.assertEqual(get_collision_normal((140, 102), rect), (0.0, -1.0))
        self.assertEqual(get_collision_normal((178, 110), rect), (1.0, 0.0))


if __name__ == "__main__":
    unittest.main()
