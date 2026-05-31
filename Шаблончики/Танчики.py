import pygame
import random

pygame.init()

# НАЛАШТУВАННЯ ВІКНА ТА СІТКИ
# TILE - базовий розмір однієї клітинки (тайлу) на екрані у пікселях.
# Вся гра будується на сітці 26 на 26 клітинок.
TILE = 24
COLS, ROWS = 26, 26
GAME_W = COLS * TILE
GAME_H = ROWS * TILE
SIDE_W = 164
WIN_W = GAME_W + SIDE_W
WIN_H = GAME_H
FPS = 30

# НАПРЯМКИ РУХУ
# Використовуємо кути (в градусах) для зручного обертання картинок.
# В Pygame 0 градусів дивиться вгору, і обертання йде проти годинникової стрілки.
UP, LEFT, DOWN, RIGHT = 0, 90, 180, 270

# Словники швидкостей. Залежно від напрямку, ми множимо швидкість танка
# на ці значення (1, 0 або -1), щоб знати, по якій осі йому рухатись.
VX = {UP: 0, RIGHT: 1, DOWN: 0, LEFT: -1}
VY = {UP: -1, RIGHT: 0, DOWN: 1, LEFT: 0}

BG_COLOR = (16, 16, 16)
HUD_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Танчики: Карта та Класи")
clock = pygame.time.Clock()

# КЛАСИ ПРОТИВНИКІВ
# Зберігаємо характеристики різних ворогів у словниках.
# Це дозволяє легко додавати нові типи без зміни основного коду.
ENEMY_TYPES = [
    {"speed": 2, "hp": 1, "points": 100, "color": (200, 48, 48)},
    {"speed": 4, "hp": 1, "points": 200, "color": (55, 185, 65)},
    {"speed": 1, "hp": 3, "points": 400, "color": (78, 78, 200)}
]
# Ймовірності появи (60% для звичайного, 25% для швидкого, 15% для важкого)
ENEMY_WEIGHTS = [0.60, 0.25, 0.15]

# ДИЗАЙН РІВНЯ (ТЕКСТОВА МАПА)
# Кожен символ відповідає за конкретний об'єкт на карті.
# @ - сталь, # - цегла, S - спавн ворогів, P - спавн гравця, E - Орел
LEVEL = [
    "@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "@S.........S...........S.@",
    "@..##..##..@@@@..##..##..@",
    "@..##..##..@@@@..##..##..@",
    "@..##..##..####..##..##..@",
    "@..##..##........##..##..@",
    "@..##..##...##...##..##..@",
    "@......##...##...##......@",
    "@......##...##...##......@",
    "@..@@..##........##..@@..@",
    "@..@@..##...##...##..@@..@",
    "@...........##...........@",
    "@...####..........####...@",
    "@...####..........####...@",
    "@........@@@@@@@@........@",
    "@........@@@@@@@@........@",
    "@..##..##........##..##..@",
    "@..##..##........##..##..@",
    "@..##..##...##...##..##..@",
    "@..##..##...##...##..##..@",
    "@..##..##...##...##..##..@",
    "@...........##...........@",
    "@.......###.##.###.......@",
    "@.......#........#.......@",
    "@...P...#...E....#.......@",
    "@@@@@@@@@@@@@@@@@@@@@@@@@@"
]

# ФУНКЦІЇ ДЛЯ КАРТИНОК
def create_placeholder(color):
    # Створює квадрат-заглушку з "дулом", якщо картинка не знайдена
    surf = pygame.Surface((TILE - 2, TILE - 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, TILE - 2, TILE - 2))
    pygame.draw.rect(surf, (50, 50, 50), (TILE // 2 - 3, 0, 4, TILE // 2))
    return surf

def colorize(image, color):
    # Накладає кольоровий фільтр на оригінальну картинку ворога
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

# Спроба завантажити справжні картинки
try:
    img_player_base = pygame.image.load("player.png").convert_alpha()
    img_enemy_base = pygame.image.load("enemy.png").convert_alpha()
    img_player_base = pygame.transform.scale(img_player_base, (TILE - 2, TILE - 2))
    img_enemy_base = pygame.transform.scale(img_enemy_base, (TILE - 2, TILE - 2))
    USE_IMAGES = True
except FileNotFoundError:
    USE_IMAGES = False

# КЛАСИ ОБ'ЄКТІВ
class Wall:
    def __init__(self, col, row, kind):
        self.rect = pygame.Rect(col * TILE, row * TILE, TILE, TILE)
        self.kind = kind
        # Цегла має 2 ХП, сталь має -1 (вважається безсмертною)
        self.hp = 2 if kind == "#" else -1
        self.alive = True

    def hit(self):
        if self.hp > 0:
            self.hp -= 1
            if self.hp <= 0:
                self.alive = False

    def draw(self, surf):
        if self.kind == "#":
            pygame.draw.rect(surf, (165, 72, 32), self.rect)
            pygame.draw.rect(surf, (88, 36, 14), self.rect, 1)
        else:
            pygame.draw.rect(surf, (108, 128, 148), self.rect)
            pygame.draw.rect(surf, (58, 82, 100), self.rect, 2)

class Eagle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.alive = True

    def draw(self, surf):
        color = (220, 190, 0) if self.alive else (110, 60, 60)
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.circle(surf, (0, 0, 0), self.rect.center, 5)

class Bullet:
    def __init__(self, x, y, direction, is_player):
        self.rect = pygame.Rect(x - 2, y - 2, 4, 4)
        # Швидкість по осях визначається напрямком
        self.vx = VX[direction] * 6
        self.vy = VY[direction] * 6
        self.is_player = is_player
        self.alive = True

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Знищуємо кулю, якщо вона вилетіла за екран
        if not (0 < self.rect.x < GAME_W and 0 < self.rect.y < GAME_H):
            self.alive = False

    def draw(self, surf):
        color = (255, 255, 120) if self.is_player else (255, 128, 78)
        pygame.draw.rect(surf, color, self.rect)

class Tank:
    def __init__(self, x, y, is_player, stats=None):
        self.rect = pygame.Rect(x, y, TILE - 2, TILE - 2)
        self.is_player = is_player
        self.direction = UP if is_player else DOWN
        self.alive = True
        self.fire_cd = 0

        # Ініціалізація характеристик гравця або типу ворога
        if is_player:
            self.speed = 2
            self.hp = 1
            self.points = 0
            color = (235, 215, 0)
            self.image = img_player_base if USE_IMAGES else create_placeholder(color)
        else:
            self.speed = stats["speed"]
            self.hp = stats["hp"]
            self.points = stats["points"]
            color = stats["color"]
            self.image = colorize(img_enemy_base, color) if USE_IMAGES else create_placeholder(color)

    def move(self, dx, dy, walls, tanks):
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Не даємо танку виїхати за межі карти
        self.rect.x = max(0, min(GAME_W - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(GAME_H - self.rect.height, self.rect.y))

        # Перевірка зіткнень зі стінами та іншими танками
        collision = False
        for w in walls:
            if w.alive and self.rect.colliderect(w.rect):
                collision = True
        for t in tanks:
            if t.alive and t is not self and self.rect.colliderect(t.rect):
                collision = True

        # Якщо є зіткнення, відкочуємо координати назад
        if collision:
            self.rect.x, self.rect.y = old_x, old_y
            return False
        return True

    def shoot(self):
        # Затримка між пострілами (Cooldown)
        if self.fire_cd <= 0:
            self.fire_cd = 30
            return Bullet(self.rect.centerx, self.rect.centery, self.direction, self.is_player)
        return None

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        # Поворот картинки на заданий кут
        rotated_img = pygame.transform.rotate(self.image, self.direction)
        img_rect = rotated_img.get_rect(center=self.rect.center)
        surf.blit(rotated_img, img_rect.topleft)

        # Індикатор ХП для важких танків (крапки на корпусі)
        if not self.is_player and self.hp > 1:
            for i in range(self.hp):
                pygame.draw.circle(surf, WHITE, (self.rect.x + 4 + i * 6, self.rect.y + 4), 2)

# ОСНОВНИЙ ЦИКЛ
def main():
    walls = []
    spawn_points = []
    player_start = (0, 0)
    eagle_start = (0, 0)

    # Читання текстової карти. enumerate дає номер рядка/стовпця і сам символ
    for row_idx, row in enumerate(LEVEL):
        for col_idx, char in enumerate(row):
            x = col_idx * TILE
            y = row_idx * TILE
            if char == '#':
                walls.append(Wall(col_idx, row_idx, "#"))
            elif char == '@':
                walls.append(Wall(col_idx, row_idx, "@"))
            elif char == 'P':
                player_start = (x, y)
            elif char == 'E':
                eagle_start = (x, y)
            elif char == 'S':
                spawn_points.append((x, y))

    player = Tank(player_start[0], player_start[1], True)
    eagle = Eagle(eagle_start[0], eagle_start[1])

    tanks = [player]
    bullets = []

    spawn_timer = 0
    score = 0
    game_over = False

    font = pygame.font.SysFont("monospace", 20, bold=True)

    # Змінна для керування циклом замість while True
    running = True

    while running:
        # 1. ОБРОБКА ПОДІЙ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main() # Запуск нової гри
                return # Завершуємо поточний цикл

        if not game_over:
            # 2. РУХ ГРАВЦЯ
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1; player.direction = UP
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1; player.direction = DOWN
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1; player.direction = LEFT
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1; player.direction = RIGHT

            if dx != 0 or dy != 0:
                player.move(dx, dy, walls, tanks)

            if keys[pygame.K_SPACE]:
                b = player.shoot()
                if b: bullets.append(b)

            # 3. СПАВН ВОРОГІВ
            spawn_timer -= 1
            if spawn_timer <= 0 and len(tanks) < 5:
                sx, sy = random.choice(spawn_points)
                # Вибираємо тип ворога на основі списку ймовірностей
                enemy_stats = random.choices(ENEMY_TYPES, weights=ENEMY_WEIGHTS)[0]

                # Перевіряємо, чи точка спавну вільна від інших танків
                spawn_rect = pygame.Rect(sx, sy, TILE - 2, TILE - 2)
                can_spawn = True
                for t in tanks:
                    if t.rect.colliderect(spawn_rect):
                        can_spawn = False

                if can_spawn:
                    tanks.append(Tank(sx, sy, False, stats=enemy_stats))
                    spawn_timer = 120
                else:
                    spawn_timer = 30 # Швидка перевірка знову, якщо зайнято

            # 4. ЛОГІКА ВОРОГІВ (Штучний Інтелект)
            for t in tanks:
                if t.fire_cd > 0: t.fire_cd -= 1

                if not t.is_player:
                    success = t.move(VX[t.direction], VY[t.direction], walls, tanks)
                    # Якщо врізався - змінює напрямок на випадковий
                    if not success:
                        t.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    # 2% шанс на постріл у кожному кадрі
                    if random.random() < 0.02:
                        b = t.shoot()
                        if b: bullets.append(b)

            # 5. ЛОГІКА КУЛЬ ТА ЗІТКНЕНЬ
            for b in bullets:
                b.update()
                if not b.alive: continue

                for w in walls:
                    if w.alive and b.rect.colliderect(w.rect):
                        w.hit()
                        b.alive = False
                        break

                if eagle.alive and b.rect.colliderect(eagle.rect):
                    eagle.alive = False
                    game_over = True

                if b.alive:
                    for t in tanks:
                        # Танк не може вбити свого (гравець ворога, ворог гравця)
                        if t.alive and b.is_player != t.is_player and b.rect.colliderect(t.rect):
                            t.take_damage()
                            b.alive = False
                            if not t.alive and not t.is_player:
                                score += t.points
                            if not t.alive and t.is_player:
                                game_over = True
                            break

            # Видалення знищених об'єктів зі списків
            bullets = [b for b in bullets if b.alive]
            tanks = [t for t in tanks if t.alive]
            walls = [w for w in walls if w.alive]

        # 6. МАЛЮВАННЯ
        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, HUD_COLOR, (GAME_W, 0, SIDE_W, WIN_H))
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_text, (GAME_W + 10, 50))

        for w in walls: w.draw(screen)
        eagle.draw(screen)
        for t in tanks: t.draw(screen)
        for b in bullets: b.draw(screen)

        if game_over:
            go_text = font.render("GAME OVER [R - Рестарт]", True, (255, 50, 50))
            screen.blit(go_text, (GAME_W // 2 - 120, GAME_H // 2))

        pygame.display.flip()
        clock.tick(FPS)

    # Вихід з Pygame відбувається лише після того, як цикл `while running` завершиться
    pygame.quit()

if __name__ == "__main__":
    main()