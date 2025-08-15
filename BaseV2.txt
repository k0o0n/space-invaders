import pygame
import random
import math
import asyncio

# Initialize pygame
pygame.init()

# Music
my_sound = pygame.mixer.Sound('media/music.mp3')
my_sound.play(-1)

# Base screen size for scaling
BASE_SCREEN_WIDTH = 900
BASE_SCREEN_HEIGHT = 600

# Initial screen size
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

# Base sizes
PLAYER_SIZE_BASE = 64
ENEMY_SIZE_BASE = 64
BULLET_SIZE_BASE = 32

# Colors
TEXT_COLOR = (180, 0, 150)  # Purple text
TEXT_BORDER_COLOR = (255, 255, 255)  # White border

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load("media/ufo.png")
pygame.display.set_icon(icon)

# Load assets
background_img_orig = pygame.image.load("media/background.png")
player_img_orig = pygame.image.load("media/player.png")
enemy_img_orig = pygame.image.load("media/enemy.png")
bullet_img_orig = pygame.image.load("media/bullet.png")

# Fonts
font_game_over = pygame.font.SysFont("comicsansms", 64, bold=True)
font_restart = pygame.font.SysFont("comicsansms", 32, bold=True)
font_score = pygame.font.SysFont("comicsansms", 28, bold=True)

# Clock
clock = pygame.time.Clock()

# Game States
PLAYING = "playing"
GAME_OVER = "game_over"
PAUSED = "paused"


def render_text_with_border(text, font, color, border_color):
    base = font.render(text, True, color)
    border = pygame.Surface((base.get_width() + 2, base.get_height() + 2), pygame.SRCALPHA)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                border.blit(font.render(text, True, border_color), (dx + 1, dy + 1))
    border.blit(base, (1, 1))
    return border


def scale_background(bg_img, width, height):
    return pygame.transform.scale(bg_img, (width, height))


def scale_value(value, axis):
    if axis == "x":
        return value * SCREEN_WIDTH / BASE_SCREEN_WIDTH
    else:
        return value * SCREEN_HEIGHT / BASE_SCREEN_HEIGHT


def scale_image(img, width, height):
    return pygame.transform.scale(img, (int(width), int(height)))


class Player:
    def __init__(self):
        self.size_base = PLAYER_SIZE_BASE
        self.speed_base = 0.55
        self.x = (SCREEN_WIDTH - self.size_base) / 2
        self.y = SCREEN_HEIGHT - self.size_base - scale_value(20, "y")
        self.left_pressed = False
        self.right_pressed = False
        self.last_key = None
        self.update_scaled()

    def update_scaled(self):
        self.size = scale_value(self.size_base, "y")
        self.image = scale_image(player_img_orig, self.size, self.size)
        self.speed = self.speed_base * SCREEN_WIDTH / BASE_SCREEN_WIDTH
        # Keep player at bottom
        self.y = SCREEN_HEIGHT - self.size - scale_value(20, "y")

    def update(self, dt):
        if self.last_key == "left" and self.left_pressed:
            self.x -= self.speed * dt
        elif self.last_key == "right" and self.right_pressed:
            self.x += self.speed * dt
        self.x = max(0, min(SCREEN_WIDTH - self.size, self.x))

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def reset_position(self):
        self.x = (SCREEN_WIDTH - self.size) / 2
        self.y = SCREEN_HEIGHT - self.size - scale_value(20, "y")


class Enemy:
    def __init__(self, speed=0.3):
        self.size_base = ENEMY_SIZE_BASE
        self.speed_base = speed
        self.x = random.randint(0, SCREEN_WIDTH - self.size_base)
        self.y = random.randint(int(scale_value(50, "y")), int(scale_value(150, "y")))
        self.x_change_base = self.speed_base * random.choice([1, -1])
        self.y_change_base = 40
        self.update_scaled()

    def update_scaled(self):
        self.size = scale_value(self.size_base, "y")
        self.image = scale_image(enemy_img_orig, self.size, self.size)
        self.x_change = self.x_change_base * (SCREEN_WIDTH / BASE_SCREEN_WIDTH)
        self.y_change = scale_value(self.y_change_base, "y")

    def update(self, dt):
        self.x += self.x_change * dt
        if self.x <= 0:
            self.x = 0
            self.x_change *= -1
            self.y += self.y_change
        elif self.x >= SCREEN_WIDTH - self.size:
            self.x = SCREEN_WIDTH - self.size
            self.x_change *= -1
            self.y += self.y_change

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def reset(self, speed):
        self.__init__(speed=speed)


class Bullet:
    def __init__(self):
        self.size_base = BULLET_SIZE_BASE
        self.speed_base = 2
        self.x = 0
        self.y = 0
        self.state = "ready"
        self.update_scaled()

    def update_scaled(self):
        self.size = scale_value(self.size_base, "y")
        self.image = scale_image(bullet_img_orig, self.size, self.size)
        self.speed = self.speed_base * (SCREEN_HEIGHT / BASE_SCREEN_HEIGHT)

    def fire(self, player_x, player_y):
        self.x = player_x + (scale_value(PLAYER_SIZE_BASE, "y") - self.size) / 2
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
        self.enemies = [Enemy()]
        self.state = PLAYING
        self.score = 0
        self.base_speed = 0.3
        self.speed_increment = 0.01

    def check_collision(self, obj1_x, obj1_y, obj2_x, obj2_y, threshold_base):
        scale_factor = (SCREEN_WIDTH + SCREEN_HEIGHT) / (BASE_SCREEN_WIDTH + BASE_SCREEN_HEIGHT)
        distance = math.sqrt((obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2)
        return distance < threshold_base * scale_factor

    def update(self, dt):
        if self.state != PLAYING:
            return
        self.player.update(dt)
        self.bullet.update(dt)
        current_speed = self.base_speed + (self.score * self.speed_increment)

        for enemy in self.enemies:
            enemy.update(dt)

        for enemy in self.enemies:
            if self.bullet.state == "fire" and self.check_collision(
                    self.bullet.x + self.bullet.size / 2,
                    self.bullet.y + self.bullet.size / 2,
                    enemy.x + enemy.size / 2,
                    enemy.y + enemy.size / 2,
                    27):
                self.bullet.state = "ready"
                enemy.reset(speed=current_speed)
                self.score += 1
                break

        for enemy in self.enemies:
            if self.check_collision(
                    self.player.x + self.player.size / 2,
                    self.player.y + self.player.size / 2,
                    enemy.x + enemy.size / 2,
                    enemy.y + enemy.size / 2,
                    40):
                self.state = GAME_OVER
                break

        expected_enemy_count = 1 + (self.score // 10)
        if len(self.enemies) < expected_enemy_count:
            self.enemies.append(Enemy(speed=current_speed))

    def draw_info_text(self, text, pos, font=font_restart, color=TEXT_COLOR):
        text_surface = render_text_with_border(text, font, color, TEXT_BORDER_COLOR)
        screen.blit(text_surface, pos)

    def draw_pause_info(self):
        lines = [
            "Controls:",
            "Left / Right: Move",
            "Space: Shoot",
            "P: Resume",
            "R: Restart",
            "",
            "Mechanics:",
            "Enemy speed increases every 1 point",
            "New enemy spawns every 10 points"
        ]
        y_offset = int(SCREEN_HEIGHT * 0.25)
        line_height = int(SCREEN_HEIGHT * 0.05)
        for line in lines:
            text_surface = render_text_with_border(line, font_score, TEXT_COLOR, TEXT_BORDER_COLOR)
            x_pos = (SCREEN_WIDTH - text_surface.get_width()) // 2
            screen.blit(text_surface, (x_pos, y_offset))
            y_offset += line_height

    def draw_score(self):
        score_text = render_text_with_border(f"Score: {self.score}", font_score, TEXT_COLOR, TEXT_BORDER_COLOR)
        screen.blit(score_text, (10, 10))

    def draw(self):
        screen.blit(scale_background(background_img_orig, SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0))

        if self.state == PLAYING:
            self.player.draw()
            self.bullet.draw()
            for enemy in self.enemies:
                enemy.draw()
            self.draw_score()
            text_surface = render_text_with_border("Press P to Pause", font_restart, TEXT_COLOR, TEXT_BORDER_COLOR)
            screen.blit(text_surface, (SCREEN_WIDTH - text_surface.get_width() - 10, 10))

        elif self.state == GAME_OVER:
            screen.fill((50, 0, 0))
            game_over_text = render_text_with_border("GAME OVER", font_game_over, TEXT_COLOR, TEXT_BORDER_COLOR)
            screen.blit(game_over_text, ((SCREEN_WIDTH - game_over_text.get_width()) // 2,
                                         int(SCREEN_HEIGHT * 0.3)))
            self.draw_info_text("Press R to Restart", ((SCREEN_WIDTH - 300) // 2, int(SCREEN_HEIGHT * 0.5)))
            self.draw_score()

        elif self.state == PAUSED:
            self.player.draw()
            self.bullet.draw()
            for enemy in self.enemies:
                enemy.draw()
            self.draw_score()
            text_surface = render_text_with_border("Press P to Pause", font_restart, TEXT_COLOR, TEXT_BORDER_COLOR)
            screen.blit(text_surface, (SCREEN_WIDTH - text_surface.get_width() - 10, 10))
            pause_text = render_text_with_border("PAUSED", font_game_over, TEXT_COLOR, TEXT_BORDER_COLOR)
            screen.blit(pause_text, ((SCREEN_WIDTH - pause_text.get_width()) // 2, int(SCREEN_HEIGHT * 0.1)))
            self.draw_pause_info()

    def reset(self):
        self.__init__()

    def rescale_objects(self):
        self.player.update_scaled()
        self.bullet.update_scaled()
        for enemy in self.enemies:
            enemy.update_scaled()


# ================= Main Async Game Loop =================
async def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen
    game = Game()
    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                game.rescale_objects()
                game.player.reset_position()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.player.left_pressed = True
                    game.player.last_key = "left"
                elif event.key == pygame.K_RIGHT:
                    game.player.right_pressed = True
                    game.player.last_key = "right"
                elif event.key == pygame.K_SPACE:
                    if game.bullet.state == "ready" and game.state == PLAYING:
                        game.bullet.fire(game.player.x, game.player.y)
                elif event.key == pygame.K_p:
                    game.state = PAUSED if game.state == PLAYING else PLAYING
                elif event.key == pygame.K_r:
                    game.reset()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.player.left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    game.player.right_pressed = False

        game.update(dt)
        game.draw()
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


# Run the game
asyncio.run(main())
