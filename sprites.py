import pygame
import random
from constants import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity = 5
        self.color = color # Store color for 3D rendering

    def update(self, keys, up, down, left, right):
        if keys[up]:
            self.rect.y -= self.velocity
        if keys[down]:
            self.rect.y += self.velocity
        if keys[left]:
            self.rect.x -= self.velocity
        if keys[right]:
            self.rect.x += self.velocity

        self.constrain()

    def constrain(self):
        # Keep in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class BotPlayer(Player):
    def __init__(self, x, y, color, difficulty="MEDIUM"):
        super().__init__(x, y, color)
        self.target_ball = None
        self.difficulty = difficulty
        
        # Set velocity based on difficulty
        if difficulty == "EASY":
            self.velocity = 3
            self.reaction_delay = 0.2  # Slower reactions
        elif difficulty == "MEDIUM":
            self.velocity = 5
            self.reaction_delay = 0.1
        elif difficulty == "HARD":
            self.velocity = 7
            self.reaction_delay = 0.0  # Instant reactions

    def update(self, ball):
        # Simple AI: Follow the ball
        # For easy mode, add some randomness
        if self.difficulty == "EASY" and random.random() < self.reaction_delay:
            return  # Skip this update sometimes
        
        if ball.rect.centerx < self.rect.centerx:
            self.rect.x -= self.velocity
        if ball.rect.centerx > self.rect.centerx:
            self.rect.x += self.velocity
        if ball.rect.centery < self.rect.centery:
            self.rect.y -= self.velocity
        if ball.rect.centery > self.rect.centery:
            self.rect.y += self.velocity
        
        self.constrain()

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Z-axis
        self.z = 0
        self.velocity_z = 0
        
        self.friction = FRICTION

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # Gravity
        if self.z > 0:
            self.velocity_z -= GRAVITY
            self.z += self.velocity_z
            if self.z < 0:
                self.z = 0
                self.velocity_z *= -0.5 # Bounce on ground

        # Bounce off walls
        if self.rect.left <= 0:
            # Check if in goal
            if GOAL_Y_TOP < self.rect.centery < GOAL_Y_BOTTOM:
                pass # Allow to go through
            else:
                self.velocity_x *= -1
                if self.rect.left < 0: self.rect.left = 0
        
        if self.rect.right >= SCREEN_WIDTH:
            # Check if in goal
            if GOAL_Y_TOP < self.rect.centery < GOAL_Y_BOTTOM:
                pass # Allow to go through
            else:
                self.velocity_x *= -1
                if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
            
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.velocity_y *= -1
            # Keep inside
            if self.rect.top < 0: self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT
