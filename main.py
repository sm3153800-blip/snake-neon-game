import pygame
import random
import sys
import math
from collections import deque

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 960, 720
CELL = 24
GRID_W = WIDTH // CELL
GRID_H = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake Worlds")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("arial", 52, bold=True)
font_big = pygame.font.SysFont("arial", 32, bold=True)
font_med = pygame.font.SysFont("arial", 24, bold=True)
font_small = pygame.font.SysFont("arial", 17, bold=True)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WORLDS = [
    {
        "name": "Cyber Neon",
        "bg": (8, 10, 22),
        "grid": (28, 40, 58),
        "head": (90, 255, 210),
        "body": (30, 180, 160),
        "tail": (10, 120, 100),
        "food": (255, 70, 180),
        "obstacle": (120, 50, 150),
        "accent": (0, 255, 180),
        "desc": "Futuristic digital maze"
    },
    {
        "name": "Volcanic Rush",
        "bg": (30, 18, 12),
        "grid": (90, 40, 24),
        "head": (255, 175, 60),
        "body": (220, 110, 25),
        "tail": (140, 65, 20),
        "food": (255, 110, 210),
        "obstacle": (120, 40, 25),
        "accent": (255, 160, 50),
        "desc": "Fiery hot arena"
    },
    {
        "name": "Aqua Drift",
        "bg": (8, 30, 45),
        "grid": (22, 62, 90),
        "head": (90, 255, 255),
        "body": (40, 170, 210),
        "tail": (10, 90, 120),
        "food": (100, 255, 180),
        "obstacle": (30, 80, 120),
        "accent": (85, 220, 255),
        "desc": "Balanced water lanes"
    },
    {
        "name": "Void Orbit",
        "bg": (12, 8, 25),
        "grid": (42, 30, 60),
        "head": (220, 130, 255),
        "body": (150, 90, 210),
        "tail": (90, 70, 160),
        "food": (255, 100, 200),
        "obstacle": (80, 40, 120),
        "accent": (200, 110, 255),
        "desc": "Asteroid field"
    },
]


class SnakeGame:
    def __init__(self):
        self.state = "menu"
        self.world_index = 0
        self.menu_index = 0
        self.reset_game()
        self.menu_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(110)]

    def reset_game(self):
        self.snake = deque([
            (GRID_W // 2, GRID_H // 2),
            (GRID_W // 2 - 1, GRID_H // 2),
            (GRID_W // 2 - 2, GRID_H // 2),
        ])
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.tick = 0
        self.game_over = False
        self.obstacles = []
        self.food = self.spawn_food()
        self.particles = []
        self.generate_world_layout()
        self.state = "playing"

    def choose_world(self, index):
        self.world_index = index % len(WORLDS)
        self.menu_index = self.world_index

    def generate_world_layout(self):
        self.obstacles = []

        if self.world_index == 0:
            for x in range(5, GRID_W - 5, 8):
                for y in range(2, GRID_H - 2, 7):
                    if (x, y) not in self.snake and random.random() < 0.42:
                        self.obstacles.append((x, y))
        elif self.world_index == 1:
            for i in range(0, GRID_W, 7):
                for j in range(0, GRID_H, 6):
                    if random.random() < 0.26 and (i, j) not in self.snake:
                        self.obstacles.append((i, j))
        elif self.world_index == 2:
            for i in range(0, GRID_W, 10):
                if i % 2 == 0:
                    for j in range(1, GRID_H - 1, 3):
                        if random.random() < 0.22:
                            self.obstacles.append((i, j))
        elif self.world_index == 3:
            for _ in range(45):
                x = random.randint(1, GRID_W - 2)
                y = random.randint(1, GRID_H - 2)
                if (x, y) not in self.snake:
                    self.obstacles.append((x, y))

        self.food = self.spawn_food()

    def spawn_food(self):
        while True:
            x = random.randint(1, GRID_W - 2)
            y = random.randint(1, GRID_H - 2)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                return (x, y)

    def create_particles(self, pos, count=16):
        palette = WORLDS[self.world_index]
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(1.5, 5)
            self.particles.append({
                "x": pos[0] * CELL + CELL / 2,
                "y": pos[1] * CELL + CELL / 2,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20, 40),
                "color": palette["food"],
            })

    def update_particles(self):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            p["vx"] *= 0.98
            p["vy"] *= 0.98
            if p["life"] <= 0:
                self.particles.remove(p)

    def update(self):
        if self.state != "playing":
            return

        self.tick += 1
        speed = 10 + self.level
        delay = max(5, 18 - speed)

        if self.tick >= delay:
            self.tick = 0
            if (self.next_direction[0], self.next_direction[1]) != (-self.direction[0], -self.direction[1]):
                self.direction = self.next_direction

            head_x, head_y = self.snake[0]
            new_head = (head_x + self.direction[0], head_y + self.direction[1])

            if new_head[0] < 0 or new_head[0] >= GRID_W or new_head[1] < 0 or new_head[1] >= GRID_H:
                self.state = "gameover"
                return

            if new_head in self.snake:
                self.state = "gameover"
                return

            if new_head in self.obstacles:
                self.state = "gameover"
                return

            self.snake.appendleft(new_head)

            if new_head == self.food:
                self.score += 1
                self.level = 1 + self.score // 3
                self.create_particles(new_head, 18)
                self.food = self.spawn_food()
            else:
                self.snake.pop()

        self.update_particles()

    def draw_background(self):
        palette = WORLDS[self.world_index]
        screen.fill(palette["bg"])
        t = pygame.time.get_ticks() * 0.02

        if self.world_index == 0:
            for i in range(12):
                y = (i * 70 + (t * 18) % 70) % HEIGHT
                pygame.draw.line(screen, palette["grid"], (0, y), (WIDTH, y), 2)
        elif self.world_index == 1:
            for i in range(14):
                y = (i * 60 + (t * 12) % 60) % HEIGHT
                pygame.draw.line(screen, palette["grid"], (0, y), (WIDTH, y), 3)
        elif self.world_index == 2:
            for i in range(15):
                offset = int(math.sin(t + i) * 16)
                pygame.draw.line(screen, palette["grid"], (0, i * 52 + offset), (WIDTH, i * 52 + offset), 2)
        elif self.world_index == 3:
            for i in range(70):
                x = (i * 37 + (t * 10)) % WIDTH
                y = (i * 23 + (t * 14)) % HEIGHT
                radius = 1 + (i % 3)
                pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), radius)

    def draw_grid(self):
        palette = WORLDS[self.world_index]
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, palette["grid"], (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, palette["grid"], (0, y), (WIDTH, y), 1)

    def draw_obstacles(self):
        palette = WORLDS[self.world_index]
        for x, y in self.obstacles:
            rect = pygame.Rect(x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(screen, palette["obstacle"], rect, border_radius=5)
            pygame.draw.rect(screen, palette["accent"], rect, 1, border_radius=5)

    def draw_food(self):
        palette = WORLDS[self.world_index]
        fx = self.food[0] * CELL + CELL // 2
        fy = self.food[1] * CELL + CELL // 2
        pulse = 8 + abs(math.sin(pygame.time.get_ticks() / 200)) * 4
        pygame.draw.circle(screen, palette["food"], (int(fx), int(fy)), int(pulse), 3)
        pygame.draw.circle(screen, palette["food"], (int(fx), int(fy)), 6)

    def draw_snake(self):
        palette = WORLDS[self.world_index]
        body = list(self.snake)

        for i, (x, y) in enumerate(body):
            px = x * CELL + CELL // 2
            py = y * CELL + CELL // 2
            size = CELL - 5
            glow = 8 if i == 0 else 5

            if i == 0:
                head_color = palette["head"]
                pygame.draw.circle(screen, head_color, (px, py), 13)
                pygame.draw.circle(screen, (255, 255, 255), (px, py), 12, 2)

                dx, dy = self.direction
                perp_x = -dy
                perp_y = dx
                eye_offset = 5
                eye_l = 2.4
                eye1 = (px + dx * eye_offset + perp_x * 4, py + dy * eye_offset + perp_y * 3)
                eye2 = (px + dx * eye_offset - perp_x * 4, py + dy * eye_offset - perp_y * 3)
                pygame.draw.circle(screen, (0, 0, 0), (int(eye1[0]), int(eye1[1])), 2)
                pygame.draw.circle(screen, (0, 0, 0), (int(eye2[0]), int(eye2[1])), 2)
            else:
                color = palette["body"] if i < len(body) - 1 else palette["tail"]
                rect = pygame.Rect(x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4)
                pygame.draw.rect(screen, color, rect, border_radius=7)
                pygame.draw.rect(screen, (255, 255, 255), rect, 1, border_radius=7)

                if i == len(body) - 1:
                    tail_x = x * CELL + CELL // 2
                    tail_y = y * CELL + CELL // 2
                    pygame.draw.circle(screen, palette["tail"], (tail_x, tail_y), 6)

        # trailing glow around head
        hx, hy = self.snake[0]
        pygame.draw.circle(screen, palette["accent"], (hx * CELL + CELL // 2, hy * CELL + CELL // 2), 18, 2)

    def draw_particles(self):
        for p in self.particles:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), max(1, int(p["life"] / 12)))

    def draw_hud(self):
        palette = WORLDS[self.world_index]
        score_text = font_med.render(f"Score: {self.score}", True, palette["accent"])
        level_text = font_med.render(f"Level: {self.level}", True, palette["accent"])
        world_text = font_small.render(WORLDS[self.world_index]["name"], True, palette["accent"])
        screen.blit(score_text, (20, 18))
        screen.blit(level_text, (20, 52))
        screen.blit(world_text, (WIDTH - 200, 18))

    def draw_gameover(self):
        palette = WORLDS[self.world_index]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        text = font_big.render("GAME OVER", True, palette["food"])
        sub = font_med.render(f"Score: {self.score}   |   Level: {self.level}", True, palette["accent"])
        tip = font_small.render("Press R to restart or M to return to the menu", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 90))
        screen.blit(sub, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
        screen.blit(tip, (WIDTH // 2 - 200, HEIGHT // 2 + 40))

    def draw_menu(self):
        screen.fill((7, 8, 22))

        for x, y in self.menu_stars:
            pygame.draw.circle(screen, (180, 180, 255), (x, y), 1)

        title = font_title.render("NEON SNAKE", True, (95, 255, 220))
        screen.blit(title, (WIDTH // 2 - 220, 50))

        subtitle = font_med.render("Choose a world", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - 110, 125))

        y = 200
        for i, world in enumerate(WORLDS):
            box = pygame.Rect(180, y, 600, 85)
            active = i == self.menu_index
            if active:
                pygame.draw.rect(screen, world["accent"], box, 3, border_radius=18)
                pygame.draw.rect(screen, (25, 25, 35), box, border_radius=18)
            else:
                pygame.draw.rect(screen, (18, 18, 30), box, border_radius=18)
                pygame.draw.rect(screen, (80, 80, 99), box, 1, border_radius=18)

            name = font_big.render(world["name"], True, world["accent"] if active else (200, 200, 200))
            desc = font_small.render(world["desc"], True, (220, 220, 220))
            screen.blit(name, (220, y + 20))
            screen.blit(desc, (220, y + 56))
            y += 110

        help_text = font_small.render("Arrow keys to move | Enter to play | Q to quit", True, (180, 255, 200))
        screen.blit(help_text, (WIDTH // 2 - 250, HEIGHT - 60))


def main():
    game = SnakeGame()
    running = True
    paused = False

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.state == "menu":
                    if event.key == pygame.K_UP:
                        game.menu_index = (game.menu_index - 1) % len(WORLDS)
                        game.world_index = game.menu_index
                    elif event.key == pygame.K_DOWN:
                        game.menu_index = (game.menu_index + 1) % len(WORLDS)
                        game.world_index = game.menu_index
                    elif event.key == pygame.K_RETURN:
                        game.reset_game()
                    elif event.key == pygame.K_q:
                        running = False

                elif game.state == "playing":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game.next_direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game.next_direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        game.next_direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game.next_direction = (1, 0)
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_m:
                        game.state = "menu"
                        paused = False
                    elif event.key == pygame.K_q:
                        running = False

                elif game.state == "gameover":
                    if event.key == pygame.K_r:
                        game.reset_game()
                    elif event.key == pygame.K_m:
                        game.state = "menu"
                    elif event.key == pygame.K_q:
                        running = False

        if game.state == "menu":
            game.draw_menu()
        elif game.state == "playing":
            if not paused:
                game.update()
            game.draw_background()
            game.draw_grid()
            game.draw_obstacles()
            game.draw_food()
            game.draw_snake()
            game.draw_particles()
            game.draw_hud()

            if paused:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                pause_text = font_title.render("PAUSED", True, WORLDS[game.world_index]["accent"])
                screen.blit(pause_text, (WIDTH // 2 - 150, HEIGHT // 2 - 30))

        elif game.state == "gameover":
            game.draw_background()
            game.draw_grid()
            game.draw_obstacles()
            game.draw_food()
            game.draw_snake()
            game.draw_particles()
            game.draw_hud()
            game.draw_gameover()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
