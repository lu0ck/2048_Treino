import pygame
import random

pygame.init()

# --- Constantes ---
GRID_SIZE = 4
TILE_SIZE = 100
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FONT_SIZE = 40
FPS = 60

# --- Cores ---
COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    'bg': (187, 173, 160),
    'text': (119, 110, 101),
    'text_light': (249, 246, 242)
}

# --- Lógica base ---
def create_grid():
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def add_new_tile(grid):
    empty = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if grid[i][j] == 0]
    if empty:
        i, j = random.choice(empty)
        grid[i][j] = 2 if random.random() < 0.9 else 4

def compress_line(line):
    new_line = [num for num in line if num != 0]
    i = 0
    while i < len(new_line) - 1:
        if new_line[i] == new_line[i + 1]:
            new_line[i] *= 2
            new_line.pop(i + 1)
        else:
            i += 1
    return new_line + [0] * (GRID_SIZE - len(new_line))

def move_left(grid):
    return [compress_line(row) for row in grid]

def move_right(grid):
    return [compress_line(row[::-1])[::-1] for row in grid]

def move_up(grid):
    t = list(map(list, zip(*grid)))
    t2 = move_left(t)
    return list(map(list, zip(*t2)))

def move_down(grid):
    t = list(map(list, zip(*grid)))
    t2 = move_right(t)
    return list(map(list, zip(*t2)))

def grids_equal(a, b):
    return all(r1 == r2 for r1, r2 in zip(a, b))

def is_game_over(grid):
    if any(0 in row for row in grid):
        return False
    for fn in (move_left, move_right, move_up, move_down):
        if not grids_equal(grid, fn(grid)):
            return False
    return True

def get_score(grid):
    return sum(sum(row) for row in grid)

# --- Cálculo de movimentos + novo grid (com mapeamento correto por direção) ---
def compute_move_and_moves(grid, direction):
    N = GRID_SIZE
    new_grid = [[0]*N for _ in range(N)]
    moves = []  # cada item: {"from":(i0,j0), "to":(i1,j1), "value":v, "merge":bool}

    if direction in ("left", "right"):
        for i in range(N):
            line = grid[i]

            if direction == "left":
                indices = list(range(N))  # 0..N-1
                to_index = lambda k: k
            else:  # right
                indices = list(range(N-1, -1, -1))  # N-1..0
                to_index = lambda k: N-1-k

            # remove zeros mantendo ordem da varredura
            entries = [(line[j], j) for j in indices if line[j] != 0]

            k = 0
            idx = 0
            while idx < len(entries):
                v1, j1 = entries[idx]
                if idx + 1 < len(entries) and entries[idx+1][0] == v1:
                    v2, j2 = entries[idx+1]
                    dest_j = to_index(k)
                    new_grid[i][dest_j] = v1 * 2
                    # dois tiles caminham para o mesmo destino
                    moves.append({"from": (i, j1), "to": (i, dest_j), "value": v1, "merge": True})
                    moves.append({"from": (i, j2), "to": (i, dest_j), "value": v2, "merge": True})
                    idx += 2
                else:
                    dest_j = to_index(k)
                    new_grid[i][dest_j] = v1
                    moves.append({"from": (i, j1), "to": (i, dest_j), "value": v1, "merge": False})
                    idx += 1
                k += 1

    else:  # up / down
        for j in range(N):
            col = [grid[i][j] for i in range(N)]

            if direction == "up":
                indices = list(range(N))
                to_index = lambda k: k
            else:  # down
                indices = list(range(N-1, -1, -1))
                to_index = lambda k: N-1-k

            entries = [(col[i], i) for i in indices if col[i] != 0]

            k = 0
            idx = 0
            while idx < len(entries):
                v1, i1 = entries[idx]
                if idx + 1 < len(entries) and entries[idx+1][0] == v1:
                    v2, i2 = entries[idx+1]
                    dest_i = to_index(k)
                    new_grid[dest_i][j] = v1 * 2
                    moves.append({"from": (i1, j), "to": (dest_i, j), "value": v1, "merge": True})
                    moves.append({"from": (i2, j), "to": (dest_i, j), "value": v2, "merge": True})
                    idx += 2
                else:
                    dest_i = to_index(k)
                    new_grid[dest_i][j] = v1
                    moves.append({"from": (i1, j), "to": (dest_i, j), "value": v1, "merge": False})
                    idx += 1
                k += 1

    # remove movimentos "parados" (from == to) para não animar tile que não se moveu
    moves = [m for m in moves if m["from"] != m["to"]]
    return new_grid, moves

# --- Desenho (com/sem animações) ---
def draw_grid_base(screen, grid, font):
    screen.fill(COLORS['bg'])
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            value = grid[i][j]
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLORS.get(value, COLORS[2048]), rect)
            if value != 0:
                color = COLORS['text_light'] if value >= 8 else COLORS['text']
                text = font.render(str(value), True, color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def draw_grid_with_animations(screen, grid, font, animations):
    # desenha apenas os tiles "fixos", exceto destinos de animações (para não duplicar)
    screen.fill(COLORS['bg'])

    # destinos que vão receber tiles em movimento
    end_cells = {(a["to"][0], a["to"][1]) for a in animations}

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            value = grid[i][j]
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if (i, j) in end_cells:
                # não desenha o tile final enquanto anima (será coberto pelos que se movem)
                pygame.draw.rect(screen, COLORS[0], rect)  # fundo da célula
                continue

            pygame.draw.rect(screen, COLORS.get(value, COLORS[2048]), rect)
            if value != 0:
                color = COLORS['text_light'] if value >= 8 else COLORS['text']
                text = font.render(str(value), True, color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    # desenha os tiles animando (cada um com seu progresso)
    finished = []
    for a in animations:
        progress = a["frame"] / a["duration"]
        if progress >= 1:
            progress = 1
            finished.append(a)

        (si, sj) = a["from"]
        (ei, ej) = a["to"]

        sx, sy = sj * TILE_SIZE, si * TILE_SIZE
        ex, ey = ej * TILE_SIZE, ei * TILE_SIZE

        x = sx + (ex - sx) * progress
        y = sy + (ey - sy) * progress

        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, COLORS.get(a["value"], COLORS[2048]), rect)
        color = COLORS['text_light'] if a["value"] >= 8 else COLORS['text']
        text = font.render(str(a["value"]), True, color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

        a["frame"] += 1

    for a in finished:
        animations.remove(a)

# --- Game Over (fade) ---
def draw_game_over(screen, font, grid, alpha):
    # desenha o tabuleiro "parado"
    draw_grid_base(screen, grid, font)
    # overlay escuro
    overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(alpha)
    screen.blit(overlay, (0, 0))
    # texto
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(text, text_rect)

# --- Main ---
def main():
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, FONT_SIZE, bold=True)

    grid = create_grid()
    add_new_tile(grid)
    add_new_tile(grid)

    animations = []          # animações ativas
    spawn_pending = False    # adicionar novo tile após terminar animação
    game_over = False
    game_over_alpha = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # só aceita tecla quando NÃO está animando e não está em game over
            if event.type == pygame.KEYDOWN and not animations and not game_over:
                direction = None
                if event.key in (pygame.K_LEFT, pygame.K_a): direction = "left"
                elif event.key in (pygame.K_RIGHT, pygame.K_d): direction = "right"
                elif event.key in (pygame.K_UP, pygame.K_w): direction = "up"
                elif event.key in (pygame.K_DOWN, pygame.K_s): direction = "down"

                if direction:
                    new_grid, moves = compute_move_and_moves(grid, direction)
                    if not grids_equal(grid, new_grid):
                        grid = new_grid

                        # cria animações a partir dos moves
                        animations.clear()
                        for m in moves:
                            animations.append({
                                "from": m["from"],
                                "to": m["to"],
                                "value": m["value"],   # valor original (pré-fusão) andando
                                "merge": m["merge"],
                                "frame": 0,
                                "duration": 8          # ~0.13s em 60 FPS
                            })
                        spawn_pending = True  # só adiciona tile novo após animar

        # pós-animação: adiciona o novo tile e checa game over
        if not animations and spawn_pending and not game_over:
            add_new_tile(grid)
            spawn_pending = False
            if is_game_over(grid):
                game_over = True

        # desenha
        if game_over:
            if game_over_alpha < 180:
                game_over_alpha += 5
            draw_game_over(screen, font, grid, game_over_alpha)
        else:
            if animations:
                draw_grid_with_animations(screen, grid, font, animations)
            else:
                draw_grid_base(screen, grid, font)

        pygame.display.set_caption(f"2048 - Score: {get_score(grid)}")
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
