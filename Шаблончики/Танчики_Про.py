import pygame
import random

pygame.init()

# ─── НАЛАШТУВАННЯ ─────────────────────────────────────────────────────────────
TILE = 24
COLS, ROWS = 26, 26
GAME_W = COLS * TILE  # 624
GAME_H = ROWS * TILE  # 624
SIDE_W = 164
WIN_W = GAME_W + SIDE_W  # 788
WIN_H = GAME_H  # 624
FPS = 60

UP, LEFT, DOWN, RIGHT = 0, 90, 180, 270
VX = {UP: 0, RIGHT: 1, DOWN: 0, LEFT: -1}
VY = {UP: -1, RIGHT: 0, DOWN: 1, LEFT: 0}

BG_COLOR = (16, 16, 16)
HUD_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Танчики: Карта та Класи")
clock = pygame.time.Clock()

# ─── КЛАСИ ПРОТИВНИКІВ ────────────────────────────────────────────────────────
ENEMY_TYPES = [
    # basic - звичайний (Шанс появи більший)
    {"speed": 2, "hp": 1, "points": 100, "color": (200, 48, 48)},
    # fast - швидкий, але слабкий
    {"speed": 4, "hp": 1, "points": 200, "color": (55, 185, 65)},
    # heavy - повільний, але броньований (3 ХП)
    {"speed": 1, "hp": 3, "points": 400, "color": (78, 78, 200)}
]
# Ймовірності появи (60% базовий, 25% швидкий, 15% важкий)
ENEMY_WEIGHTS = [0.60, 0.25, 0.15]

# ─── ДИЗАЙН РІВНЯ (ТЕКСТОВА МАПА) ─────────────────────────────────────────────
# @ - сталь (не пробивається)
# # - цегла (пробивається)
# S - точка спавну ворогів
# P - точка спавну гравця
# E - Орел (база)
# . - порожнє місце
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


# ─── ФУНКЦІЇ ДЛЯ КАРТИНОК ─────────────────────────────────────────────────────
def create_placeholder(color):
    surf = pygame.Surface((TILE - 2, TILE - 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, TILE - 2, TILE - 2))
    pygame.draw.rect(surf, (50, 50, 50), (TILE // 2 - 3, 0, 4, TILE // 2))
    return surf


def colorize(image, color):
    """Створює копію картинки і накладає на неї відтінок кольору"""
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


try:
    img_player_base = pygame.image.load("player.png").convert_alpha()
    img_enemy_base = pygame.image.load("enemy.png").convert_alpha()
    img_player_base = pygame.transform.scale(img_player_base, (TILE - 2, TILE - 2))
    img_enemy_base = pygame.transform.scale(img_enemy_base, (TILE - 2, TILE - 2))
    USE_IMAGES = True
except FileNotFoundError:
    USE_IMAGES = False


# ─── КЛАСИ ────────────────────────────────────────────────────────────────────
class Wall:
    def __init__(self, col, row, kind):
        self.rect = pygame.Rect(col * TILE, row * TILE, TILE, TILE)
        self.kind = kind
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
        self.vx = VX[direction] * 6
        self.vy = VY[direction] * 6
        self.is_player = is_player
        self.alive = True

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
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

        # Налаштування характеристик
        if is_player:
            self.speed = 2
            self.hp = 1
            self.points = 0
            color = (235, 215, 0)  # Жовтий для гравця
            if USE_IMAGES:
                self.image = img_player_base
            else:
                self.image = create_placeholder(color)
        else:
            self.speed = stats["speed"]
            self.hp = stats["hp"]
            self.points = stats["points"]
            color = stats["color"]
            if USE_IMAGES:
                # Фарбуємо картинку залежно від типу ворога
                self.image = colorize(img_enemy_base, color)
            else:
                self.image = create_placeholder(color)

    def _check_collision(self, walls, tanks):
        """Допоміжна функція: перевіряє, чи не врізався танк у стіну або інший танк"""
        for w in walls:
            if w.alive and self.rect.colliderect(w.rect):
                return True
        for t in tanks:
            if t.alive and t is not self and self.rect.colliderect(t.rect):
                return True
        return False

    def move(self, dx, dy, walls, tanks):
        old_x, old_y = self.rect.x, self.rect.y

        # 1. ПРОСТЕ АВТО-ВИРІВНЮВАННЯ (Cornering Assistance)
        # Якщо ми їдемо вліво/вправо (dx != 0), вирівнюємо танк по вертикалі (Y)
        if dx != 0:
            offset = (self.rect.y - 1) % TILE

            if offset != 0:
                if offset <= TILE // 2:
                    self.rect.y -= 1
                else:
                    self.rect.y += 1

                    # Якщо ми їдемо вгору/вниз (dy != 0), вирівнюємо танк по горизонталі (X)
        if dy != 0:
            offset = (self.rect.x - 1) % TILE

            if offset != 0:
                if offset <= TILE // 2:
                    self.rect.x -= 1
                else:
                    self.rect.x += 1

                    # Якщо авто-вирівнювання випадково засунуло нас у стіну - скасовуємо його
        if self._check_collision(walls, tanks):
            self.rect.x, self.rect.y = old_x, old_y

        # 2. ОСНОВНИЙ РУХ ВПЕРЕД
        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Обмеження екрану
        self.rect.x = max(0, min(GAME_W - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(GAME_H - self.rect.height, self.rect.y))

        # Якщо рух вперед призвів до зіткнення — скасовуємо ТІЛЬКИ рух вперед
        if self._check_collision(walls, tanks):
            self.rect.x, self.rect.y = old_x, old_y
            return False

        return True

    def shoot(self):
        if self.fire_cd <= 0:
            self.fire_cd = 30
            return Bullet(self.rect.centerx, self.rect.centery, self.direction, self.is_player)
        return None

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        rotated_img = pygame.transform.rotate(self.image, self.direction)
        img_rect = rotated_img.get_rect(center=self.rect.center)
        surf.blit(rotated_img, img_rect.topleft)

        # Малюємо індикатор ХП для важких танків
        if not self.is_player and self.hp > 1:
            for i in range(self.hp):
                pygame.draw.circle(surf, WHITE, (self.rect.x + 4 + i * 6, self.rect.y + 4), 2)


# ─── ОСНОВНИЙ ЦИКЛ ────────────────────────────────────────────────────────────
def main():
    walls = []
    spawn_points = []
    player_start = (0, 0)
    eagle_start = (0, 0)

    # Парсимо (зчитуємо) нашу текстову карту
    for row_idx, row in enumerate(LEVEL):
        for col_idx, char in enumerate(row):
            x = col_idx * TILE
            y = row_idx * TILE
            if char == '#':
                walls.append(Wall(col_idx, row_idx, "#"))
            elif char == '@':
                walls.append(Wall(col_idx, row_idx, "@"))
            elif char == 'P':
                # +1 піксель, щоб ідеально відцентрувати танк розміром 22px у клітинці 24px
                player_start = (x + 1, y + 1)
            elif char == 'E':
                eagle_start = (x, y)
            elif char == 'S':
                # +1 піксель для ворогів
                spawn_points.append((x + 1, y + 1))

    player = Tank(player_start[0], player_start[1], True)
    eagle = Eagle(eagle_start[0], eagle_start[1])

    tanks = [player]
    bullets = []

    spawn_timer = 0
    score = 0
    game_over = False

    font = pygame.font.SysFont("monospace", 20, bold=True)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()
                return

        if not game_over:
            # Рух гравця
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1;
                player.direction = UP
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1;
                player.direction = DOWN
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1;
                player.direction = LEFT
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1;
                player.direction = RIGHT

            if dx != 0 or dy != 0:
                player.move(dx, dy, walls, tanks)

            if keys[pygame.K_SPACE]:
                b = player.shoot()
                if b: bullets.append(b)

            # Спавн ворогів
            spawn_timer -= 1
            if spawn_timer <= 0 and len(tanks) < 5:
                sx, sy = random.choice(spawn_points)
                enemy_stats = random.choices(ENEMY_TYPES, weights=ENEMY_WEIGHTS)[0]

                spawn_rect = pygame.Rect(sx, sy, TILE - 2, TILE - 2)
                can_spawn = True
                for t in tanks:
                    if t.rect.colliderect(spawn_rect):
                        can_spawn = False

                if can_spawn:
                    tanks.append(Tank(sx, sy, False, stats=enemy_stats))
                    spawn_timer = 120
                else:
                    spawn_timer = 30

            # Логіка ворогів
            for t in tanks:
                if t.fire_cd > 0: t.fire_cd -= 1

                if not t.is_player:
                    success = t.move(VX[t.direction], VY[t.direction], walls, tanks)
                    if not success:
                        t.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                    if random.random() < 0.02:
                        b = t.shoot()
                        if b: bullets.append(b)

            # Логіка куль
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
                        if t.alive and b.is_player != t.is_player and b.rect.colliderect(t.rect):
                            t.take_damage()
                            b.alive = False
                            if not t.alive and not t.is_player:
                                score += t.points
                            if not t.alive and t.is_player:
                                game_over = True
                            break

            bullets = [b for b in bullets if b.alive]
            tanks = [t for t in tanks if t.alive]
            walls = [w for w in walls if w.alive]

        # МАЛЮВАННЯ
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


if __name__ == "__main__":
    main()