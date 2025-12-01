import pygame

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Football Game"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Physics
FPS = 60
FRICTION = 0.98
GRAVITY = 0.5

# 3D / 2.5D Projection
FOV = 300
CAMERA_HEIGHT = 400
CAMERA_DISTANCE = 200

# Network
SERVER_IP = "127.0.0.1"
PORT = 5555

# Gameplay
GOAL_WIDTH = 150
GOAL_Y_TOP = (SCREEN_HEIGHT - GOAL_WIDTH) // 2
GOAL_Y_BOTTOM = (SCREEN_HEIGHT + GOAL_WIDTH) // 2
