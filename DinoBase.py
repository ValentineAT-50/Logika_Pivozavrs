# підключення pygame
import pygame
from random import randint
# кольори
YELLOW = (200, 200, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


FPS = 50


# налаштування Pygame
pygame.init()
screen = pygame.display.set_mode((500, 500))


image_player_run1 = pygame.image.load("images/DinoRun1.png").convert_alpha()
image_player_run2 = pygame.image.load("images/DinoRun2.png").convert_alpha()
image_player_jump = pygame.image.load("images/DinoJump.png").convert_alpha()


image_cactus = pygame.image.load("images/SmallCactus1.png")
image_cloud = pygame.image.load("images/Cloud.png")
image_ground = pygame.image.load("images/Track.png")




# текстова позначка
class Label:
    def __init__(self, x, y, size, color="black", default_text="text"):
        self.font = pygame.font.Font(None, size)
        self.coord = (x, y)
        self.color = color
        self.set_text(default_text)


    def set_text(self, text):
        self.image = self.font.render(text, True, self.color)


    def draw(self, screen):
        screen.blit(self.image, self.coord)




# гравець, вбудоване керування
class Player:
    def __init__(self, x, y, images):
        self.images = images
        self.image = image_player_run1


        self.animation_count = 0
        self.current_image = 0


        self.max_y = y
        self.rect = pygame.Rect(
            x, y, self.image.get_width(), self.image.get_height())
        self.velocity = 0
        self.GRAVITY = 0.7
        self.in_air = False


    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.left -= 5
        elif keys[pygame.K_RIGHT]:
            self.rect.left += 5


        if keys[pygame.K_SPACE] and not self.in_air:
            self.velocity = 15
            self.in_air = True
            self.animation_count = 0
            self.current_image = 0
            self.image = self.images[2]


        if self.in_air:
            self.rect.top -= self.velocity
            self.velocity -= self.GRAVITY
            if self.rect.top >= self.max_y:
                self.in_air = False
                self.rect.top = self.max_y
        else:
            self.animation_count += 1
            if self.animation_count >= 15:
                self.animation_count = 0
                self.current_image += 1
                if self.current_image > 1:
                    self.current_image = 0
                self.image = self.images[self.current_image]


    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))
        # pygame.draw.rect(screen, RED, self.rect, 2)




# кактус, що рухається ліворуч
class Cactus:
    def __init__(self, x, y):
        super().__init__()
        self.image = image_cactus
        self.rect = pygame.Rect(
            x, y, self.image.get_width(), self.image.get_height())


    def update(self):
        self.rect.left -= 2


    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))
        # pygame.draw.rect(screen, RED, self.rect, 2)




# клас хмари, яка рухається ліворуч
class Cloud:
    def __init__(self):
        super().__init__()
        self.image = image_cloud
        self.rect = pygame.Rect(500, randint(
            20, 300), self.image.get_width(), self.image.get_height())


    def update(self):
        self.rect.left -= 2


    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))




#  трек та хмари, все що не взаємодіє з гравцем (візуальні ефекти)
class Enviroment:
    def __init__(self, x, y):
        super().__init__()
        self.image = image_ground
        self.rect = pygame.Rect(
            x, y, self.image.get_width(), self.image.get_height())
        self.ground_count = 0
        self.clouds = []
        self.cloud_count = 0
        self.cloud_count_max = 100


    def update(self):
        self.rect.left -= 2
        self.ground_count += 1
        if self.ground_count == 800:
            self.ground_count = 0
            self.rect.left = 0


        self.cloud_count += 1
        if self.cloud_count == self.cloud_count_max:
            self.cloud_count = 0
            self.cloud_count_max = randint(80, 200)
            self.clouds.append(Cloud())


        for c in self.clouds:
            c.update()
            if c.rect.right < 0:
                self.clouds.remove(c)


    def draw(self, screen):
        screen.blit(self.image, (self.rect.left, self.rect.top))
        for c in self.clouds:
            c.draw(screen)




#  кактуси, обробка руху та видалення, ще є котроль статистики
class CactusGroup:
    def __init__(self, label):
        self.label = label
        self.count = 0
        self.count_max = 0
        self.obstacles = []
        self.score = 0


    def update(self):
        if self.count == 0:
            self.count_max = randint(150, 250)
        self.count += 1


        if self.count == self.count_max:
            self.count = 0
            self.obstacles.append(Cactus(500, 400))


        for o in self.obstacles:
            o.update()
            if o.rect.right < 0:
                self.obstacles.remove(o)
                self.score += 100
                self.label.set_text(f"Score: {self.score}")


    def draw(self, screen):
        for o in self.obstacles:
            o.draw(screen)




# ігрові об'єкти та ігровий цикл
label = Label(300, 20, 28, BLACK, f"Score: {0}")
cactus_group = CactusGroup(label)
player = Player(100, 380, (image_player_run1,
                image_player_run2, image_player_jump))
enviroment = Enviroment(0, 460)




# створення годинника
clock = pygame.time.Clock()
running = True


while running:
    # обробка подій
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


    # заливка екрана кольором, відображення прямокутників
    screen.fill(WHITE)
    player.update()
    enviroment.update()
    cactus_group.update()


    for cactus in cactus_group.obstacles:
        if cactus.rect.colliderect(player.rect):
            print("gameover")


    enviroment.draw(screen)
    cactus_group.draw(screen)
    label.draw(screen)
    player.draw(screen)


    # оновлення дисплея та обмеження частоти
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()
