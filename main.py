import pygame
import random
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
PLAYER_SIZE = 64
ENEMY_SIZE = 64
BULLET_SIZE = 32

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("media/ufo.png")
pygame.display.set_icon(icon)

# Load assets
background = pygame.image.load("media/background.png")
player_img = pygame.image.load("media/player.png")
enemy_img = pygame.image.load("media/enemy.png")
bullet_img = pygame.image.load("media/bullet.png")

# Fonts
font_game_over = pygame.font.SysFont("comicsansms", 64)
font_restart = pygame.font.SysFont("comicsansms", 32)
font_score = pygame.font.SysFont("comicsansms", 28)

# Clock
clock = pygame.time.Clock()

# Game States
PLAYING = "playing"
GAME_OVER = "game_over"
PAUSED = "paused"


class Player:
    def __init__(self):
        self.image = player_img
        self.x = (SCREEN_WIDTH - PLAYER_SIZE) // 2
        self.y = 480
        self.speed = 0.4
        self.x_change = 0
        self.left_pressed = False
        self.right_pressed = False
        self.last_key = None

    def update(self, dt):
        if self.last_key == "left" and self.left_pressed:
            self.x_change = -self.speed * dt
        elif self.last_key == "right" and self.right_pressed:
            self.x_change = self.speed * dt
        else:
            self.x_change = 0

        self.x += self.x_change
        self.x = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, self.x))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Enemy:
    def __init__(self):
        self.image = enemy_img
        self.speed = 0.3
        self.x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
        self.y = random.randint(50, 150)
        self.x_change = self.speed * random.choice([1, -1])
        self.y_change = 40

    def update(self, dt):
        self.x += self.x_change * dt
        if self.x <= 0 or self.x >= SCREEN_WIDTH - ENEMY_SIZE:
            self.x_change *= -1
            self.y += self.y_change

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def reset(self):
        self.__init__()


class Bullet:
    def __init__(self):
        self.image = bullet_img
        self.speed = 2
        self.x = 0
        self.y = 0
        self.state = "ready"

    def fire(self, player_x, player_y):
        self.x = player_x + (PLAYER_SIZE - BULLET_SIZE) // 2
        self.y = player_y
        self.state = "fire"

    def update(self, dt):
        if self.state == "fire":
            self.y -= self.speed * dt
            if self.y < 0:
                self.state = "ready"

    def draw(self):
        if self.state == "fire":
            screen.blit(self.image, (self.x, self.y))


class Game:
    def __init__(self):
        self.player = Player()
        self.bullet = Bullet()
        self.enemies = [Enemy(), Enemy()]
        self.state = PLAYING
        self.score = 0

    def check_collision(self, obj1_x, obj1_y, obj2_x, obj2_y, threshold):
        distance = math.sqrt((obj1_x - obj2_x)**2 + (obj1_y - obj2_y)**2)
        return distance < threshold

    def update(self, dt):
        if self.state == PLAYING:
            self.player.update(dt)
            self.bullet.update(dt)
            for enemy in self.enemies:
                enemy.update(dt)

            for enemy in self.enemies:
                if self.bullet.state == "fire" and self.check_collision(
                    self.bullet.x + BULLET_SIZE // 2,
                    self.bullet.y + BULLET_SIZE // 2,
                    enemy.x + ENEMY_SIZE // 2,
                    enemy.y + ENEMY_SIZE // 2,
                    27):
                    self.bullet.state = "ready"
                    enemy.reset()
                    self.score += 1
                    break

            for enemy in self.enemies:
                if self.check_collision(
                    self.player.x + PLAYER_SIZE // 2,
                    self.player.y + PLAYER_SIZE // 2,
                    enemy.x + ENEMY_SIZE // 2,
                    enemy.y + ENEMY_SIZE // 2,
                    40):
                    self.state = GAME_OVER
                    break

    def draw_background(self):
        screen.blit(background, (0, 0))

    def draw_restart_text(self, pos):
        x, y = pos
        restart_text = font_restart.render("Press R to Restart", True, (255, 255, 0))
        screen.blit(restart_text, (x, y))

    def draw_score(self):
        score_text = font_score.render(f"Score: {self.score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 10))

    def draw_game_over_text(self):
        game_over_text = font_game_over.render("GAME OVER", True, (255, 255, 255))
        screen.blit(game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2, 200))

    def draw_paused_text(self):
        pause_text = font_game_over.render("PAUSED", True, (255, 255, 0))
        screen.blit(pause_text, ((SCREEN_WIDTH - pause_text.get_width()) // 2, 250))

    def draw_entities(self):
        self.player.draw()
        self.bullet.draw()
        for enemy in self.enemies:
            enemy.draw()

    def draw(self):
        if self.state == PLAYING:
            self.draw_background()
            self.draw_restart_text((600, 5))
            self.draw_entities()
            self.draw_score()

        elif self.state == GAME_OVER:
            screen.fill((50, 0, 0))
            self.draw_game_over_text()
            self.draw_restart_text((600, 621))
            self.draw_score()

        elif self.state == PAUSED:
            self.draw_background()
            self.draw_entities()
            self.draw_score()
            self.draw_restart_text((600, 5))
            self.draw_paused_text()

    def reset(self):
        self.__init__()


# Main game loop
game = Game()
running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game.state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.player.left_pressed = True
                    game.player.last_key = "left"
                elif event.key == pygame.K_RIGHT:
                    game.player.right_pressed = True
                    game.player.last_key = "right"
                elif event.key == pygame.K_SPACE and game.bullet.state == "ready":
                    game.bullet.fire(game.player.x, game.player.y)
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_p:
                    game.state = PAUSED
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.player.left_pressed = False
                    if game.player.last_key == "left":
                        game.player.last_key = "right" if game.player.right_pressed else None
                elif event.key == pygame.K_RIGHT:
                    game.player.right_pressed = False
                    if game.player.last_key == "right":
                        game.player.last_key = "left" if game.player.left_pressed else None

        elif game.state == PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game.state = PLAYING
                elif event.key == pygame.K_r:
                    game.reset()

        elif game.state == GAME_OVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()

    if game.state == PLAYING:
        game.update(dt)

    game.draw()
    pygame.display.update()

pygame.quit()