#!/usr/bin/env python3
"""Test script to check if all imports work correctly."""

import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    print("Testing imports...")
    
    # Test constants
    from breakout.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK
    print("✓ Constants imported successfully")
    
    # Test entities
    from breakout.entities import Paddle, Ball, Brick, PowerUp
    print("✓ Entities imported successfully")
    
    # Test game
    from breakout.game import Game, GameState
    print("✓ Game class imported successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
