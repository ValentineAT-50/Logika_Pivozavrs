import pygame
import math

BULLET_COLOR = (255, 255, 0)


class Bullet:
    def __init__(self, x, y, target_x, target_y, damage):
        self.x = float(x)
        self.y = float(y)
        self.speed = 8.0
        self.damage = damage
        self.active = True

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        self.dx = (dx / dist) * self.speed if dist > 0 else 0
        self.dy = (dy / dist) * self.speed if dist > 0 else 0

        self.target_rect = pygame.Rect(target_x - 4, target_y - 4, 8, 8)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.target_rect.collidepoint(self.x, self.y):
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, BULLET_COLOR, (int(self.x), int(self.y), 3, 3))


class Unit:
    def __init__(self, x, y, name, unit_type, team, color):
        self.x = float(x)
        self.y = float(y)
        self.size = 8
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.name = name
        self.unit_type = unit_type
        self.team = team
        self.color = color

        self.max_hp = 100
        self.hp = 100
        self.speed = 2.0
        self.attack_range = 120
        self.damage = 10
        self.max_cooldown = 30
        self.cooldown = 0

        self.target_pos = None

    def update(self, all_units, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.target_pos:
            tx, ty = self.target_pos
            dx = tx - (self.x + self.size / 2)
            dy = ty - (self.y + self.size / 2)
            dist = math.hypot(dx, dy)

            if dist > self.speed:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            else:
                self.target_pos = None

        for other in all_units:
            if other is self or other.hp <= 0:
                continue

            cx1, cy1 = self.x + self.size / 2, self.y + self.size / 2
            cx2, cy2 = other.x + other.size / 2, other.y + other.size / 2
            dx = cx1 - cx2
            dy = cy1 - cy2
            dist = math.hypot(dx, dy)

            min_dist = self.size + 2

            if dist < min_dist:

                if dist == 0:
                    dx = 1.0
                    dy = 0.0
                    dist = 1.0

                overlap = min_dist - dist
                push_x = (dx / dist) * overlap * 0.5
                push_y = (dy / dist) * overlap * 0.5

                self.x += push_x
                self.y += push_y

        self.rect.topleft = (int(self.x), int(self.y))

        if self.cooldown == 0:
            nearest_enemy = None
            min_dist = self.attack_range

            for u in all_units:
                if u.team != self.team and u.hp > 0:
                    dist = math.hypot((u.x + u.size / 2) - (self.x + self.size / 2),
                                      (u.y + u.size / 2) - (self.y + self.size / 2))
                    if dist < min_dist:
                        min_dist = dist
                        nearest_enemy = u

            if nearest_enemy:
                bullets.append(
                    Bullet(self.rect.centerx, self.rect.centery, nearest_enemy.rect.centerx, nearest_enemy.rect.centery,
                           self.damage))
                nearest_enemy.hp -= self.damage
                self.cooldown = self.max_cooldown

    def draw(self, surface, is_selected):
        if self.hp <= 0:
            return

        pygame.draw.rect(surface, self.color, self.rect)
        hp_width = int((max(0, self.hp) / self.max_hp) * self.size)
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 4, self.size, 2))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 4, hp_width, 2))

        if is_selected and self.team == 1:
            pygame.draw.rect(surface, (0, 255, 0), self.rect.inflate(4, 4), 1)

    def check_hover(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos) and self.hp > 0


class Tank(Unit):
    def __init__(self, x, y, name, team, color):
        super().__init__(x, y, name, "Танк", team, color)
        self.max_hp = 250
        self.hp = 250
        self.speed = 1.2
        self.attack_range = 160
        self.damage = 45
        self.max_cooldown = 70


class BMP(Unit):
    def __init__(self, x, y, name, team, color):
        super().__init__(x, y, name, "БМП", team, color)
        self.max_hp = 90
        self.hp = 90
        self.speed = 2.8
        self.attack_range = 110
        self.damage = 8
        self.max_cooldown = 12
