import pygame
import random
import sys

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 960, 720
CELL = 24
GRID_W = WIDTH // CELL
GRID_H = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pysurface = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake Worlds")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont("arial", 48, bold=True)
font_big = pygame.font.SysFont("arial", 32, bold=True)
font_med = pygame.font.SysFont("arial", 24, bold=True)
font_small = pygame.font.SysFont("arial", 18, bold=True)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WORLDS = [
    {
        "name": "Cyber Neon",
        "bg": (8, 10, 22),
        "grid": (28, 40, 58),
        "head": (80, 255, 200),
        "body": (20, 180, 160),
        "food": (255, 70, 180),
        "obstacle": (120, 50, 150),
        "accent": (0, 255, 180),
        "desc": "Futuristic digital maze"
    },
    {
        "name": "Volcanic Rush",
        "bg": (30, 18, 12),
        "grid": (90, 40, 24),
        "head": (255, 170, 50),
        "body": (200, 90, 20),
        "food": (255, 110, 190),
        "obstacle": (120, 40, 25),
        "accent": (255, 160, 50),
        "desc": "Fiery hot arena"
    },
    {
        "name": "Aqua Drift",
        "bg": (8, 30, 45),
        "grid": (22, 62, 90),
        "head": (80, 255, 255),
        "body": (35, 170, 210),
        "food": (90, 255, 180),
        "obstacle": (30, 80, 120),
        "accent": (75, 220, 255),
        "desc": "Balanced water lanes"
    },
    {
        "name": "Void Orbit",
        "bg": (12, 8, 25),
        "grid": (42, 30, 60),
        "head": (220, 130, 255),
        "body": (140, 90, 200),
        "food": (255, 100, 200),
        "obstacle": (80, 40, 120),
        "accent": (200, 110, 255),
        "desc": "Asteroid field"
    },
]


class SnakeGame:
    def __init__(self):
        self.state = "menu"  # menu, playing, gameover
        self.world_index = 0
        self.menu_index = 0
        self.reset_game()

    def reset_game(self):
        self.snake = [(GRID_W // 2, GRID_H // 2), (GRID_W // 2 - 1, GRID_H // 2), (GRID_W // 2 - 2, GRID_H // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.level = 1
        self.tick = 0
        self.game_over = False
        self.obstacles = []
        self.food = self.spawn_food()
        self.generate_world_layout()
        self.state = "playing"

    def choose_world(self, index):
        self.world_index = index % len(WORLDS)
        self.menu_index = self.world_index

    def generate_world_layout(self):
        world = WORLDS[self.world_index]
        self.obstacles = []

        if self.world_index == 0:  # Cyber Neon
            for x in range(6, GRID_W - 6, 9):
                for y in range(2, GRID_H - 2, 9):
                    if (x, y) not in self.snake and random.random() < 0.45:
                        self.obstacles.append((x, y))

        elif self.world_index == 1:  # Volcanic Rush
            for i in range(0, GRID_W, 8):
                for j in range(1, GRID_H, 7):
                    if (i, j) not in self.snake and random.random() < 0.35:
                        self.obstacles.append((i, j))

        elif self.world_index == 2:  # Aqua Drift
            for i in range(0, GRID_W, 10):
                if i % 2 == 0:
                    for j in range(1, GRID_H - 1, 3):
                        if random.random() < 0.25:
                            self.obstacles.append((i, j))

        elif self.world_index == 3:  # Void Orbit
            for _ in range(40):
                x = random.randint(1, GRID_W - 2)
                y = random.randint(1, GRID_H - 2)
                if (x, y) not in self.snake:
                    self.obstacles.append((x, y))

        # ensure food isn't on obstacle
        self.food = self.spawn_food()

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in self.snake and (x, y) not in self.obstacles:
                return (x, y)

    def update(self):
        if self.state != "playing":
            return

        self.tick += 1
        speed = 9 + self.level
        if self.tick >= 18 - min(speed, 14):
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

            self.snake = [new_head] + self.snake

            if new_head == self.food:
                self.score += 1
                self.level = 1 + self.score // 4
                self.food = self.spawn_food()
            else:
                self.snake.pop()

    def draw_background(self):
        palette = WORLDS[self.world_index]
        screen.fill(palette["bg"])

        # glowing stripes
        for i in range(12):
            y = (i * 80 + (pygame.time.get_ticks() // 30) % 80) % HEIGHT
            pygame.draw.line(screen, palette["grid"], (0, y), (WIDTH, y), 2)

    def draw_grid(self):
        palette = WORLDS[self.world_index]
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, palette["grid"], (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, palette["grid"], (0, y), (WIDTH, y), 1)

    def draw_food(self):
        palette = WORLDS[self.world_index]
        fx = self.food[0] * CELL + CELL // 2
        fy = self.food[1] * CELL + CELL // 2
        pygame.draw.circle(screen, palette["food"], (fx, fy), 9)
        pygame.draw.circle(screen, WHITE, (fx, fy), 4)

    def draw_obstacles(self):
        palette = WORLDS[self.world_index]
        for x, y in self.obstacles:
            rect = pygame.Rect(x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(screen, palette["obstacle"], rect, border_radius=5)
            pygame.draw.rect(screen, palette["accent"], rect, 1, border_radius=5)

    def draw_snake(self):
        palette = WORLDS[self.world_index]
        for i, (x, y) in enumerate(self.snake):
            r = pygame.Rect(x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4)
            if i == 0:
                pygame.draw.rect(screen, palette["head"], r, border_radius=6)
                pygame.draw.rect(screen, WHITE, r, 2, border_radius=6)
            else:
                pygame.draw.rect(screen, palette["body"], r, border_radius=5)
                pygame.draw.rect(screen, palette["accent"], r, 1, border_radius=5)

    def draw_hud(self):
        palette = WORLDS[self.world_index]
        score_text = font_med.render(f"Score: {self.score}", True, palette["accent"])
        level_text = font_med.render(f"Level: {self.level}", True, palette["accent"])
        world_text = font_small.render(WORLDS[self.world_index]["name"], True, palette["accent"])
        screen.blit(score_text, (20, 18))
        screen.blit(level_text, (20, 50))
        screen.blit(world_text, (WIDTH - 200, 18))

    def draw_gameover(self):
        palette = WORLDS[self.world_index]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        text = font_big.render("GAME OVER", True, palette["food"])
        sub = font_med.render(f"Score: {self.score}  |  Level: {self.level}", True, palette["accent"])
        tip = font_small.render("Press R to restart or M to return to menu", True, WHITE)

        screen.blit(text, (WIDTH // 2 - 130, HEIGHT // 2 - 80))
        screen.blit(sub, (WIDTH // 2 - 160, HEIGHT // 2 - 20))
        screen.blit(tip, (WIDTH // 2 - 200, HEIGHT // 2 + 40))

    def draw_menu(self):
        screen.fill((5, 5, 18))

        # starfield effect
        for i in range(80):
            x = (i * 31 + pygame.time.get_ticks() // 20) % WIDTH
            y = (i * 17 + pygame.time.get_ticks() // 30) % HEIGHT
            pygame.draw.circle(screen, (180, 180, 255), (x, y), 1)

        title = font_title.render("NEON SNAKE", True, (0, 255, 200))
        screen.blit(title, (WIDTH // 2 - 220, 60))

        subtitle = font_med.render("Choose a world", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - 120, 130))

        y = 220
        for i, world in enumerate(WORLDS):
            color = world["accent"] if i == self.menu_index else (180, 180, 180)
            box = pygame.Rect(220, y, 520, 80)
            if i == self.menu_index:
                pygame.draw.rect(screen, world["accent"], box, 3, border_radius=15)
                pygame.draw.rect(screen, (30, 30, 40), box, border_radius=15)
            else:
                pygame.draw.rect(screen, (25, 25, 35), box, border_radius=15)
                pygame.draw.rect(screen, (80, 80, 100), box, 1, border_radius=15)

            name = font_big.render(world["name"], True, color)
            desc = font_small.render(world["desc"], True, (220, 220, 220))
            screen.blit(name, (260, y + 18))
            screen.blit(desc, (260, y + 52))
            y += 110

        help_text = font_small.render("Arrow keys to move | Enter to play | Q to quit", True, (180, 255, 200))
        screen.blit(help_text, (WIDTH // 2 - 240, HEIGHT - 60))


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
            game.draw_hud()

            if paused:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                screen.blit(overlay, (0, 0))
                pause_text = font_title.render("PAUSED", True, WORLDS[game.world_index]["accent"])
                screen.blit(pause_text, (WIDTH // 2 - 150, HEIGHT // 2 - 40))

        elif game.state == "gameover":
            game.draw_background()
            game.draw_grid()
            game.draw_obstacles()
            game.draw_food()
            game.draw_snake()
            game.draw_hud()
            game.draw_gameover()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
