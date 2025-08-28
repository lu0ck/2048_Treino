import pygame
import random

# Inicializa Pygame
pygame.init()

# Constantes
GRID_SIZE = 4
TILE_SIZE = 100
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FONT_SIZE = 40
FPS = 60

# Cores (RGB)
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

# Função para criar uma grade vazia
def create_grid():
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Adiciona um novo tile (2 ou 4) em posição aleatória vazia
def add_new_tile(grid):
    empty_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if grid[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        grid[i][j] = 2 if random.random() < 0.9 else 4
    return grid

# Compacta uma linha para a esquerda (remove zeros e combina iguais)
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

# Move para esquerda
def move_left(grid):
    new_grid = [compress_line(row) for row in grid]
    return new_grid

# Move para direita (inverte, move esquerda, inverte de novo)
def move_right(grid):
    new_grid = [compress_line(row[::-1])[::-1] for row in grid]
    return new_grid

# Move para cima (transpõe, move esquerda, transpõe de novo)
def move_up(grid):
    transposed = list(map(list, zip(*grid)))
    new_transposed = move_left(transposed)
    return list(map(list, zip(*new_transposed)))

# Move para baixo (transpõe, move direita, transpõe de novo)
def move_down(grid):
    transposed = list(map(list, zip(*grid)))
    new_transposed = move_right(transposed)
    return list(map(list, zip(*new_transposed)))

# Verifica se grids são iguais (para saber se movimento mudou algo)
def grids_equal(grid1, grid2):
    return all(row1 == row2 for row1, row2 in zip(grid1, grid2))

# Verifica se jogo acabou (sem espaços vazios e sem movimentos possíveis)
def is_game_over(grid):
    if any(0 in row for row in grid):
        return False
    directions = [move_left, move_right, move_up, move_down]
    return all(grids_equal(grid, direction(grid)) for direction in directions)

# Calcula pontuação (soma dos tiles)
def get_score(grid):
    return sum(sum(row) for row in grid)

# Desenha a grade na tela
def draw_grid(screen, grid, font):
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

# Texto de Game Over
def draw_game_over(screen, font):
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(text, text_rect)

# Função principal do jogo
def main():
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, FONT_SIZE, bold=True)

    grid = create_grid()
    add_new_tile(grid)
    add_new_tile(grid)

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game_over:
                old_grid = [row[:] for row in grid]
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    grid = move_left(grid)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    grid = move_right(grid)
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    grid = move_up(grid)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    grid = move_down(grid)
                
                if not grids_equal(old_grid, grid):
                    add_new_tile(grid)
                
                if is_game_over(grid):
                    game_over = True

        draw_grid(screen, grid, font)
        if game_over:
            draw_game_over(screen, font)
        
        # Mostra pontuação no título
        pygame.display.set_caption(f"2048 - Score: {get_score(grid)}")
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()