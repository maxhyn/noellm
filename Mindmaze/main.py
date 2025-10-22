import pygame
import random
import time
import os
from dataclasses import dataclass
from typing import List, Tuple

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 960, 640
GRID_W, GRID_H = 24, 16         # grid size (cells)
CELL = 32                       # pixels per cell
MARGIN_X = (WIDTH - GRID_W * CELL) // 2
MARGIN_Y = (HEIGHT - GRID_H * CELL) // 2

# Gameplay
START_TIME_SECONDS = 60
FRUIT_COUNT = 10
FRUIT_BONUS_SECONDS = 20

# Colors
BG_BASE = (0, 0, 0)            # black background
PATH_COLOR = (230, 230, 240)   # unused for now (no grid)
WALL_COLOR = (255, 255, 255)   # white walls for clear visibility
PLAYER_COLOR = (255, 140, 90)
FRUIT_COLOR = (200, 20, 20)    # PolyU-themed red
GOAL_COLOR = (200, 230, 120)

pygame.init()
pygame.display.set_caption("MindMaze -Race against time")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)
font_big = pygame.font.SysFont(None, 44)
font_small = pygame.font.SysFont(None, 20)

# -----------------------------
# Maze generation (DFS backtracker)
# -----------------------------
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}

def generate_maze(w, h, seed=None):
    if seed is not None:
        random.seed(seed)
    maze = [[0 for _ in range(w)] for _ in range(h)]
    visited = [[False for _ in range(w)] for _ in range(h)]
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        x, y = stack[-1]
        neighbors = []
        for direction in (N, S, E, W):
            nx, ny = x + DX[direction], y + DY[direction]
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                neighbors.append((direction, nx, ny))
        if neighbors:
            d, nx, ny = random.choice(neighbors)
            maze[y][x] |= d
            maze[ny][nx] |= OPPOSITE[d]
            visited[ny][nx] = True
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

# -----------------------------
# Helpers
# -----------------------------
def cell_to_rect(cx, cy):
    return pygame.Rect(MARGIN_X + cx * CELL, MARGIN_Y + cy * CELL, CELL, CELL)

def draw_text_center(text, y, big=False, color=(240,240,250)):
    f = font_big if big else font
    surf = f.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

# -----------------------------
# Simple PolyU-like fruit shape
# -----------------------------
def draw_polyu_fruit(center: Tuple[int, int], r: int, color: Tuple[int, int, int]):
    cx, cy = center
    # Draw a diamond (rotated square) as a stylized red "fruit"
    points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(screen, color, points)
    # Add a small inner cutout to suggest a knot-like logo
    inner_r = int(r * 0.45)
    inner = [(cx, cy - inner_r), (cx + inner_r, cy), (cx, cy + inner_r), (cx - inner_r, cy)]
    pygame.draw.polygon(screen, BG_BASE, inner)

@dataclass
class Fruit:
    pos: Tuple[int, int]
    eaten: bool = False

# -----------------------------
# Game State
# -----------------------------
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.maze = generate_maze(GRID_W, GRID_H, seed=random.randint(0, 999999))
        self.player = [0, 0]
        self.goal = (GRID_W-1, GRID_H-1)
        self.state = "MENU"  # MENU, PLAY, WIN, LOSE, PAUSE
        self.message = "Reach the exit in time. Eat fruits for +20s."
        self.fruits = self.spawn_fruits(FRUIT_COUNT)
        self.time_left = float(START_TIME_SECONDS)
        self.start_wallclock = time.time()

    def spawn_fruits(self, count: int):
        fruits = []
        free_cells = [(x, y) for y in range(GRID_H) for x in range(GRID_W) if (x, y) not in [(0,0), self.goal]]
        random.shuffle(free_cells)
        for i in range(min(count, len(free_cells))):
            fruits.append(Fruit(pos=free_cells[i]))
        return fruits

    def neighbors_open(self, cx, cy):
        # returns list of open directions from cell
        cell = self.maze[cy][cx]
        dirs = []
        if cell & N: dirs.append((0, -1))
        if cell & S: dirs.append((0, 1))
        if cell & E: dirs.append((1, 0))
        if cell & W: dirs.append((-1, 0))
        return dirs

    def move_player(self, dx, dy):
        cx, cy = self.player
        cell = self.maze[cy][cx]
        if dx == 1 and (cell & E):
            self.player[0] += 1
        elif dx == -1 and (cell & W):
            self.player[0] -= 1
        elif dy == 1 and (cell & S):
            self.player[1] += 1
        elif dy == -1 and (cell & N):
            self.player[1] -= 1
        # Fruit collection
        for fruit in self.fruits:
            if tuple(self.player) == fruit.pos and not fruit.eaten:
                fruit.eaten = True
                self.time_left += FRUIT_BONUS_SECONDS

        # Win check
        if tuple(self.player) == self.goal:
            self.state = "WIN"

    # -----------------------------
    # Rendering
    # -----------------------------
    def draw_maze(self):
        screen.fill(BG_BASE)

        # draw walls (white on black)
        for y in range(GRID_H):
            for x in range(GRID_W):
                cell = self.maze[y][x]
                rx, ry = MARGIN_X + x*CELL, MARGIN_Y + y*CELL
                if not (cell & N):
                    pygame.draw.line(screen, WALL_COLOR, (rx, ry), (rx+CELL, ry), 4)
                if not (cell & W):
                    pygame.draw.line(screen, WALL_COLOR, (rx, ry), (rx, ry+CELL), 4)
                # draw south/east walls at borders
                if y == GRID_H-1 and not (cell & S):
                    pygame.draw.line(screen, WALL_COLOR, (rx, ry+CELL), (rx+CELL, ry+CELL), 4)
                if x == GRID_W-1 and not (cell & E):
                    pygame.draw.line(screen, WALL_COLOR, (rx+CELL, ry), (rx+CELL, ry+CELL), 4)

        # draw fruits
        for fr in self.fruits:
            if fr.eaten:
                continue
            cx, cy = fr.pos
            rect = cell_to_rect(cx, cy)
            draw_polyu_fruit(rect.center, CELL//3, FRUIT_COLOR)

        # draw goal
        gx, gy = self.goal
        grect = cell_to_rect(gx, gy)
        pygame.draw.rect(screen, GOAL_COLOR, grect.inflate(-CELL//3, -CELL//3), 0)

        # draw player
        px, py = self.player
        prect = cell_to_rect(px, py)
        pygame.draw.circle(screen, PLAYER_COLOR, prect.center, CELL//5)
        # HUD — timer and message
        draw_text_center(f"Time left: {max(0, self.time_left):.0f}s", 24, False, (220,220,230))
        draw_text_center(self.message, HEIGHT-20, False, (210,210,220))

    def draw_menu(self):
        screen.fill((16,16,22))
        draw_text_center("MindMaze -Race against time", HEIGHT//2 - 60, big=True)
        draw_text_center("Move with WASD/Arrows. Collect fruits (+20s). Reach the exit in 60s.", HEIGHT//2, False)
        draw_text_center("Press SPACE to start", HEIGHT//2 + 60, False, (210,210,220))

    def draw_win(self):
        screen.fill((20,24,24))
        draw_text_center("You reached the exit in time!", HEIGHT//2 - 20, big=True)
        draw_text_center("Press R to play again or Esc for Menu", HEIGHT//2 + 30, False)

    def draw_lose(self):
        screen.fill((24,20,20))
        draw_text_center("Time's up!", HEIGHT//2 - 20, big=True)
        draw_text_center("Press R to retry or Esc for Menu", HEIGHT//2 + 30, False)

# -----------------------------
# Utilities
# -----------------------------
def wrap_text(s, width):
    words = s.split()
    lines = []
    line = []
    count = 0
    for w in words:
        if count + len(w) + (1 if line else 0) <= width:
            line.append(w)
            count += len(w) + (1 if line else 0)
        else:
            lines.append(" ".join(line))
            line = [w]
            count = len(w)
    if line:
        lines.append(" ".join(line))
    return lines

# -----------------------------
# Main loop
# -----------------------------
def main():
    g = Game()
    running = True
    held = {pygame.K_UP:False, pygame.K_DOWN:False, pygame.K_LEFT:False, pygame.K_RIGHT:False,
            pygame.K_w:False, pygame.K_a:False, pygame.K_s:False, pygame.K_d:False}

    MOVE_TICK = 140  # ms between moves
    move_accum = 0

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if g.state == "MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    g.state = "PLAY"
                    g.message = "Find the exit. Collect fruits to add time."
            elif g.state == "PLAY":
                if event.type == pygame.KEYDOWN:
                    if event.key in held: held[event.key] = True
                    if event.key == pygame.K_ESCAPE:
                        g.state = "PAUSE"
                    elif event.key == pygame.K_r:
                        g.reset()
                if event.type == pygame.KEYUP and event.key in held:
                    held[event.key] = False

            elif g.state == "PAUSE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        g.state = "PLAY"
                    elif event.key == pygame.K_r:
                        g.reset()

            elif g.state == "WIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        g.reset()
                    elif event.key == pygame.K_ESCAPE:
                        g.state = "MENU"
            elif g.state == "LOSE":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        g.reset()
                    elif event.key == pygame.K_ESCAPE:
                        g.state = "MENU"

        # continuous movement
        if g.state == "PLAY":
            move_accum += dt
            if move_accum >= MOVE_TICK:
                move_accum = 0
                dx = dy = 0
                if held[pygame.K_LEFT] or held[pygame.K_a]: dx = -1
                elif held[pygame.K_RIGHT] or held[pygame.K_d]: dx = 1
                elif held[pygame.K_UP] or held[pygame.K_w]: dy = -1
                elif held[pygame.K_DOWN] or held[pygame.K_s]: dy = 1
                if dx or dy:
                    g.move_player(dx, dy)

        # update timer
        if g.state == "PLAY":
            g.time_left -= dt/1000.0
            if g.time_left <= 0:
                g.time_left = 0
                g.state = "LOSE"

        # draw
        if g.state == "MENU":
            g.draw_menu()
        elif g.state == "PLAY":
            g.draw_maze()
        elif g.state == "PAUSE":
            g.draw_maze()
            draw_text_center("Paused — Esc to resume, R to regenerate", HEIGHT//2, False)
        elif g.state == "WIN":
            g.draw_win()
        elif g.state == "LOSE":
            g.draw_lose()

        pygame.display.flip()

if __name__ == "__main__":
    main()
