import pygame
import math
import random

# ІНІЦІАЛІЗАЦІЯ ТА НАЛАШТУВАННЯ
pygame.init()
WIDTH, HEIGHT = 960, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Arena: Динамічні ціни")
clock = pygame.time.Clock()
FPS = 60

# КОЛЬОРИ
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 40)
PLAYER_COLOR = (50, 150, 255)
ENEMY_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 200, 0)
MENU_BG = (0, 0, 0, 200)

BTN_COLOR = (70, 70, 90)
BTN_HOVER_COLOR = (100, 100, 130)

# ЗАВАНТАЖЕННЯ ФОНУ
# Використовуємо try-except, щоб гра не вилітала з помилкою, якщо картинки немає в папці.
try:
    bg_image = pygame.image.load("background.png").convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    print("[СИСТЕМА] Фонове зображення 'background.png' успішно завантажено!")
except FileNotFoundError:
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill(BG_COLOR)
    print("\n[УВАГА] Картинка 'background.png' не підключена або не знайдена!")
    print("[СИСТЕМА] Використовується стандартний суцільний фон.\n")


# КЛАС ГРАВЦЯ
class Player:
    def __init__(self):
        # Ставимо гравця рівно по центру екрану
        self.x = float(WIDTH // 2)
        self.y = float(HEIGHT // 2)
        self.radius = 18
        self.speed = 4
        self.hp = 100
        self.max_hp = 100
        self.score = 0

        self.damage = 25
        self.fire_delay = 15
        self.fire_timer = 0

        # Динамічні ціни: ці змінні будуть збільшуватись після кожної покупки
        self.cost_dmg = 50
        self.cost_spd = 50
        self.cost_hp = 30

    def update(self, keys):
        # Базовий рух: змінюємо координати залежно від натиснутих клавіш
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed

        # Обмежуємо рух екраном, щоб гравець не міг вийти за його межі
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # Таймер стрільби зменшується щокадру. Коли він дійде до 0, можна стріляти знову.
        if self.fire_timer > 0:
            self.fire_timer -= 1

    def get_rect(self):
        # Створюємо невидимий квадрат навколо круглого гравця для спрощеної перевірки зіткнень
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, PLAYER_COLOR, (int(self.x), int(self.y)), self.radius)

        # Малюємо смужку здоров'я. Спочатку червоний фон, потім зелена смужка зверху.
        pygame.draw.rect(surf, (100, 0, 0), (WIDTH // 2 - 100, HEIGHT - 30, 200, 15))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (0, 200, 0), (WIDTH // 2 - 100, HEIGHT - 30, 200 * hp_ratio, 15))


# КЛАС КУЛІ
class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, damage):
        self.x = float(start_x)
        self.y = float(start_y)
        self.radius = 5
        self.speed = 10
        self.alive = True
        self.damage = damage

        # ТРИГОНОМЕТРІЯ: math.atan2 знаходить кут між точкою старту і ціллю (мишкою).
        # Знаючи кут, math.cos та math.sin допомагають знайти швидкість по осях X та Y.
        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Якщо куля вилітає за межі екрану, ми її "вбиваємо" (alive = False)
        if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            self.alive = False

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)


# КЛАС ВОРОГА
class Enemy:
    def __init__(self):
        # Ворог з'являється за межами екрану. Випадково обираємо одну з 4 сторін.
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.x, self.y = random.randint(0, WIDTH), -30
        elif side == "bottom":
            self.x, self.y = random.randint(0, WIDTH), HEIGHT + 30
        elif side == "left":
            self.x, self.y = -30, random.randint(0, HEIGHT)
        else:
            self.x, self.y = WIDTH + 30, random.randint(0, HEIGHT)

        self.radius = 15
        self.speed = 2
        self.max_hp = 40
        self.hp = self.max_hp
        self.alive = True

    def update(self, player):
        # ШТУЧНИЙ ІНТЕЛЕКТ: Ворог завжди вираховує кут до поточних координат гравця
        # і робить крок у його напрямку. Це створює ефект безперервного переслідування.
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surf):
        pygame.draw.circle(surf, ENEMY_COLOR, (int(self.x), int(self.y)), self.radius)

        # Міні-смужка здоров'я над кожним ворогом
        pygame.draw.rect(surf, (50, 0, 0), (self.x - 15, self.y - 25, 30, 5))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (200, 0, 0), (self.x - 15, self.y - 25, 30 * hp_ratio, 5))


# ФУНКЦІЯ ВІДМАЛЬОВУВАННЯ КНОПОК
def draw_button(surf, rect, text, font, mouse_pos, is_active=True):
    # Метод collidepoint перевіряє, чи знаходиться точка (курсор миші) всередині прямокутника
    is_hovered = rect.collidepoint(mouse_pos)

    # Змінюємо колір: сірий якщо неактивна, світліший якщо навели мишку, звичайний в іншому разі
    if not is_active:
        color = (50, 50, 50)
    else:
        color = BTN_HOVER_COLOR if is_hovered else BTN_COLOR

    # border_radius закруглює кути кнопки
    pygame.draw.rect(surf, color, rect, border_radius=8)
    pygame.draw.rect(surf, WHITE, rect, 2, border_radius=8)

    # Відцентровуємо текст рівно по центру прямокутника кнопки
    text_surf = font.render(text, True, WHITE if is_active else (150, 150, 150))
    text_rect = text_surf.get_rect(center=rect.center)
    surf.blit(text_surf, text_rect)

    return is_hovered


# ОСНОВНИЙ ЦИКЛ ГРИ
def main():
    player = Player()
    bullets = []
    enemies = []

    spawn_timer = 0
    spawn_interval = 60

    font = pygame.font.SysFont(None, 36)
    font_large = pygame.font.SysFont(None, 64)

    # Налаштування прямокутників для кнопок меню (щоб вони були по центру)
    btn_w, btn_h = 600, 50
    btn_x = WIDTH // 2 - btn_w // 2
    btn_dmg_rect = pygame.Rect(btn_x, 250, btn_w, btn_h)
    btn_spd_rect = pygame.Rect(btn_x, 320, btn_w, btn_h)
    btn_hp_rect = pygame.Rect(btn_x, 390, btn_w, btn_h)

    # Стан гри визначає, яку логіку обробляти і що малювати на екрані
    game_state = "playing"

    # Прапорець для безпечного виходу з гри замість використання sys.exit()
    running = True

    while running:
        # Отримуємо поточні координати курсора миші
        mouse_pos = pygame.mouse.get_pos()

        # 1. ОБРОБКА ПОДІЙ (Натискання клавіш та кліки миші)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Клавіша ESC працює як пауза та відкриває меню покращень
                if event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        game_state = "upgrade"
                    elif game_state == "upgrade":
                        game_state = "playing"

                # Рестарт гри після програшу
                if game_state == "gameover" and event.key == pygame.K_r:
                    main()
                    return

            # Обробка кліків лівою кнопкою миші (button == 1) по кнопках меню
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "upgrade":

                    # Купівля шкоди: перевіряємо чи клікнули по кнопці і чи вистачає грошей
                    if btn_dmg_rect.collidepoint(mouse_pos) and player.score >= player.cost_dmg:
                        player.score -= player.cost_dmg
                        player.damage += 10
                        player.cost_dmg += 20  # Ціна на наступне покращення зростає

                    # Купівля швидкості стрільби
                    if btn_spd_rect.collidepoint(mouse_pos) and player.score >= player.cost_spd:
                        if player.fire_delay > 3:  # Межа швидкості, щоб не стріляти лазером
                            player.score -= player.cost_spd
                            player.fire_delay -= 2
                            player.cost_spd += 30

                            # Купівля лікування
                    if btn_hp_rect.collidepoint(mouse_pos) and player.score >= player.cost_hp:
                        player.score -= player.cost_hp
                        # Лікуємо, але не більше ніж максимальне здоров'я
                        player.hp = min(player.hp + 30, player.max_hp)
                        player.cost_hp += 10

                        # 2. ОНОВЛЕННЯ ЛОГІКИ (Рух, стрільба, вороги)
        # Оновлюємо все тільки тоді, коли гра не на паузі і ми не програли
        if game_state == "playing":
            keys = pygame.key.get_pressed()
            player.update(keys)

            mouse_pressed = pygame.mouse.get_pressed()
            # Стрільба: якщо затиснута ліва кнопка миші і таймер дорівнює нулю
            if mouse_pressed[0] and player.fire_timer <= 0:
                bullets.append(Bullet(player.x, player.y, mouse_pos[0], mouse_pos[1], player.damage))
                player.fire_timer = player.fire_delay  # Перезапускаємо таймер затримки

            # Спавн нових ворогів
            spawn_timer -= 1
            if spawn_timer <= 0:
                enemies.append(Enemy())
                spawn_timer = spawn_interval
                # Ускладнюємо гру з часом: зменшуємо інтервал між появою ворогів
                spawn_interval = max(20, spawn_interval - 1)

            for b in bullets: b.update()

            # Очищуємо пам'ять: залишаємо в списку тільки ті кулі, які ще летять
            bullets = [b for b in bullets if b.alive]

            for enemy in enemies:
                enemy.update(player)

                # ЗІТКНЕННЯ: Ворог і Гравець
                if player.get_rect().colliderect(enemy.get_rect()):
                    player.hp -= 1
                    if player.hp <= 0:
                        game_state = "gameover"

                # ЗІТКНЕННЯ: Куля і Ворог
                for b in bullets:
                    if b.get_rect().colliderect(enemy.get_rect()):
                        enemy.hp -= b.damage
                        b.alive = False  # Куля зникає після влучання
                        if enemy.hp <= 0:
                            enemy.alive = False
                            player.score += 15  # Нараховуємо гроші за вбитого ворога
                        break  # Виходимо з перевірки куль, щоб одна куля не влучила у двох

            enemies = [e for e in enemies if e.alive]

        # 3. ВІДМАЛЬОВУВАННЯ ГРАФІКИ
        screen.blit(bg_image, (0, 0))

        # Малюємо об'єкти, якщо ми граємо або якщо ми в меню (щоб гра була на фоні меню)
        if game_state in ["playing", "upgrade"]:
            for b in bullets: b.draw(screen)
            for e in enemies: e.draw(screen)
            player.draw(screen)

            # Інтерфейс під час гри
            score_text = font.render(f"Очки покращень: {player.score}", True, WHITE)
            hint_text = font.render("[ESC] Меню покращень", True, (200, 200, 200))
            screen.blit(score_text, (10, 10))
            screen.blit(hint_text, (WIDTH - 300, 10))

        # Накладання Меню Покращень
        if game_state == "upgrade":
            # Створюємо напівпрозору поверхню для ефекту затемнення екрану
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(MENU_BG)
            screen.blit(overlay, (0, 0))

            title = font_large.render("МЕНЮ ПОКРАЩЕНЬ", True, BULLET_COLOR)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

            # f-strings (f"...") дозволяють нам вставляти змінні прямо в текст кнопки
            draw_button(screen, btn_dmg_rect, f"+10 Шкоди (Поточна: {player.damage} | Ціна: {player.cost_dmg})", font,
                        mouse_pos)

            # Перевіряємо, чи швидкість не на максимумі, щоб змінити вигляд кнопки
            if player.fire_delay > 3:
                draw_button(screen, btn_spd_rect, f"Швидкість стрільби (Ціна: {player.cost_spd})", font, mouse_pos)
            else:
                draw_button(screen, btn_spd_rect, "Швидкість стрільби (МАКСИМУМ)", font, mouse_pos, is_active=False)

            draw_button(screen, btn_hp_rect, f"Вилікувати 30 ХП (Ціна: {player.cost_hp})", font, mouse_pos)

            exit_hint = font.render("Натисніть [ESC] щоб повернутися до гри", True, (150, 150, 150))
            screen.blit(exit_hint, (WIDTH // 2 - exit_hint.get_width() // 2, 500))

        # Екран після смерті
        elif game_state == "gameover":
            go_text = font_large.render("ГРА ЗАКІНЧЕНА", True, (255, 50, 50))
            restart_txt = font.render("Натисніть R для перезапуску", True, WHITE)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 30))

        # Оновлюємо екран та контролюємо кількість кадрів на секунду
        pygame.display.flip()
        clock.tick(FPS)

    # Виходимо з Pygame, коли змінна running стає False (наприклад, при закритті вікна)
    pygame.quit()


if __name__ == "__main__":
    main()