import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 64
ENEMY_WIDTH = 64
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load('media/ufo.png')
pygame.display.set_icon(icon)

# Load images
background = pygame.image.load('media/background.png')
playerImg = pygame.image.load('media/player.png')
enemyImg = pygame.image.load('media/enemy.png')

clock = pygame.time.Clock()


# --------------------- Player Class ---------------------
class Player:
    def __init__(self, image, x, y, speed):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.move_dir = 0

    def update(self, dt):
        self.x += self.speed * self.move_dir * dt / 1000.0
        self.x = max(0, min(self.x, SCREEN_WIDTH - PLAYER_WIDTH))

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


# --------------------- Enemy Class ---------------------
class Enemy:
    def __init__(self, image, x, y, speed, y_step):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.y_step = y_step
        self.direction = random.choice([-1, 1])

    def update(self, dt):
        self.x += self.direction * self.speed * dt / 1000.0
        if self.x <= 0:
            self.x = 0
            self.direction = 1
            self.y += self.y_step
        elif self.x >= SCREEN_WIDTH - ENEMY_WIDTH:
            self.x = SCREEN_WIDTH - ENEMY_WIDTH
            self.direction = -1
            self.y += self.y_step

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


# Game entities
player = Player(playerImg, (SCREEN_WIDTH - PLAYER_WIDTH) // 2, 480, 300)
enemy = Enemy(enemyImg, random.randint(0, SCREEN_WIDTH - ENEMY_WIDTH), random.randint(50, 150), 200, 40)

# Input state tracking
left_pressed = False
right_pressed = False
last_key_pressed = None

# --------------------- Game Loop ---------------------
running = True
while running:
    dt = clock.tick(60)

    # Background
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left_pressed = True
                last_key_pressed = "left"
            if event.key == pygame.K_RIGHT:
                right_pressed = True
                last_key_pressed = "right"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_pressed = False
                if last_key_pressed == "left":
                    last_key_pressed = "right" if right_pressed else None
            if event.key == pygame.K_RIGHT:
                right_pressed = False
                if last_key_pressed == "right":
                    last_key_pressed = "left" if left_pressed else None

    # Movement logic with priority to most recent key press
    if last_key_pressed == "left" and left_pressed:
        player.move_dir = -1
    elif last_key_pressed == "right" and right_pressed:
        player.move_dir = 1
    else:
        player.move_dir = 0

    # Update and draw
    player.update(dt)
    enemy.update(dt)
    player.draw(screen)
    enemy.draw(screen)

    pygame.display.update()

# Clean exit
pygame.quit()
