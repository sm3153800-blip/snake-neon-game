import pygame
import random
import math
import sys

pygame.init()
pygame.font.init()

# --- Config --------------------------------------------------------------
WIDTH, HEIGHT = 960, 720
BOARD_MARGIN = 70
BOARD_W = WIDTH - BOARD_MARGIN * 2
BOARD_H = HEIGHT - BOARD_MARGIN * 2
CELL = 20
GRID_W = BOARD_W // CELL
GRID_H = BOARD_H // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake Retro")
clock = pygame.time.Clock()

# --- Colors --------------------------------------------------------------
BG = (3, 12, 9)
BORDER = (20, 255, 90)
GRID = (15, 38, 24)
GREEN = (90, 255, 90)
GREEN_DARK = (30, 180, 60)
RED = (255, 70, 70)
RED_DARK = (180, 30, 30)
WHITE = (255, 255, 255)
SHADOW = (0, 0, 0)

# --- Fonts ---------------------------------------------------------------
font_gameover = pygame.font.Font(None, 120)
font_score = pygame.font.Font(None, 90)
font_small = pygame.font.Font(None, 38)
font_button = pygame.font.Font(None, 44)

# --- Helper --------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(v, hi))


class SnakeGame:
    def __init__(self):
        self.state = "playing"
        self.reset()

    def reset(self):
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.snake = [(GRID_W // 2, GRID_H // 2), (GRID_W // 2 - 1, GRID_H // 2), (GRID_W // 2 - 2, GRID_H // 2)]
        self.food = self.spawn_food()
        self.score = 0
        self.speed = 8
        self.tick = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            x = random.randint(1, GRID_W - 2)
            y = random.randint(1, GRID_H - 2)
            if (x, y) not in self.snake:
                return (x, y)

    def handle_input(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.next_dir = (0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.next_dir = (0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.next_dir = (-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.next_dir = (1, 0)

        if self.state == "gameover" and key == pygame.K_SPACE:
            self.reset()
            self.state = "playing"

    def update(self):
        if self.state != "playing":
            return

        self.tick += 1
        step = max(4, 10 - self.score // 4)
        if self.tick >= step:
            self.tick = 0
            if (self.next_dir[0], self.next_dir[1]) != (-self.direction[0], -self.direction[1]):
                self.direction = self.next_dir

            head_x, head_y = self.snake[0]
            nx = head_x + self.direction[0]
            ny = head_y + self.direction[1]

            if nx < 0 or ny < 0 or nx >= GRID_W or ny >= GRID_H:
                self.state = "gameover"
                self.game_over = True
                return

            if (nx, ny) in self.snake:
                self.state = "gameover"
                self.game_over = True
                return

            self.snake.insert(0, (nx, ny))

            if (nx, ny) == self.food:
                self.score += 1
                self.food = self.spawn_food()
            else:
                self.snake.pop()

    def draw_board(self):
        # background and glowing frame
        screen.fill(BG)

        frame = pygame.Rect(BOARD_MARGIN - 18, BOARD_MARGIN - 18, BOARD_W + 36, BOARD_H + 36)
        pygame.draw.rect(screen, BORDER, frame, 4, border_radius=16)
        pygame.draw.rect(screen, BG, (BOARD_MARGIN, BOARD_MARGIN, BOARD_W, BOARD_H), border_radius=8)

        # subtle neon glow around inner board
        glow = pygame.Surface((BOARD_W, BOARD_H), pygame.SRCALPHA)
        pygame.draw.rect(glow, (20, 255, 90, 20), glow.get_rect(), border_radius=8)
        screen.blit(glow, (BOARD_MARGIN, BOARD_MARGIN))

        # grid pattern
        for x in range(0, BOARD_W + 1, CELL):
            pygame.draw.line(screen, GRID, (BOARD_MARGIN + x, BOARD_MARGIN), (BOARD_MARGIN + x, HEIGHT - BOARD_MARGIN), 1)
        for y in range(0, BOARD_H + 1, CELL):
            pygame.draw.line(screen, GRID, (BOARD_MARGIN, BOARD_MARGIN + y), (WIDTH - BOARD_MARGIN, BOARD_MARGIN + y), 1)

        # draw food
        fx = BOARD_MARGIN + self.food[0] * CELL + CELL // 2
        fy = BOARD_MARGIN + self.food[1] * CELL + CELL // 2
        pygame.draw.circle(screen, RED, (fx, fy), 7)
        pygame.draw.circle(screen, (255, 130, 130), (fx, fy), 3)

        # draw snake segments
        for i, (x, y) in enumerate(self.snake):
            px = BOARD_MARGIN + x * CELL + 2
            py = BOARD_MARGIN + y * CELL + 2
            rect = pygame.Rect(px, py, CELL - 4, CELL - 4)
            color = GREEN if i == 0 else GREEN_DARK
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, WHITE, rect, 1, border_radius=6)

            if i == 0:
                dir_x, dir_y = self.direction
                eye_offset = 5
                eye1 = (
                    px + CELL // 2 + dir_x * eye_offset + (-dir_y) * 4,
                    py + CELL // 2 + dir_y * eye_offset + dir_x * 4,
                )
                eye2 = (
                    px + CELL // 2 + dir_x * eye_offset - (-dir_y) * 4,
                    py + CELL // 2 + dir_y * eye_offset - dir_x * 4,
                )
                pygame.draw.circle(screen, (20, 20, 20), (int(eye1[0]), int(eye1[1])), 2)
                pygame.draw.circle(screen, (20, 20, 20), (int(eye2[0]), int(eye2[1])), 2)

    def draw_gameover(self):
        # dark overlay to mimic reference image
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        # big title "GAME OVER"
        text = font_gameover.render("GAME OVER", True, RED)
        text_shadow = font_gameover.render("GAME OVER", True, (180, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
        screen.blit(text_shadow, (text_rect.x + 6, text_rect.y + 6))
        screen.blit(text, text_rect)

        # score label
        score_label = font_small.render("FINAL SCORE", True, (140, 255, 140))
        score_label_rect = score_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(score_label, score_label_rect)

        # score digits glow green
        score_val = f"{self.score:05d}"
        score_text = font_score.render(score_val, True, GREEN)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 85))
        screen.blit(score_text, score_rect)

        # play again button
        btn_x = WIDTH // 2 - 160
        btn_y = HEIGHT // 2 + 170
        btn_w = 320
        btn_h = 62
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, border_radius=10)
        pygame.draw.rect(screen, GREEN, btn_rect, 3, border_radius=10)
        btn_text = font_button.render("PLAY AGAIN", True, GREEN)
        btn_text_rect = btn_text.get_rect(center=btn_rect.center)
        screen.blit(btn_text, btn_text_rect)

        # bottom note
        note = font_small.render("PRESS SPACE TO RESTART", True, (120, 255, 120))
        note_rect = note.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 245))
        screen.blit(note, note_rect)

        # small red dot at bottom like reference
        pygame.draw.circle(screen, RED_DARK, (WIDTH // 2, HEIGHT - 90), 7)

    def draw(self):
        if self.state == "playing":
            self.draw_board()
        else:
            self.draw_board()
            self.draw_gameover()


def main():
    game = SnakeGame()
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.state == "gameover":
                    game.reset()
                    game.state = "playing"
                elif game.state == "playing":
                    game.handle_input(event.key)
                elif event.key == pygame.K_m:
                    game.state = "playing"
                    game.reset()
                elif event.key == pygame.K_q:
                    running = False

        if game.state == "playing":
            game.update()

        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
