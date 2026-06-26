import pygame


class SpawnMenu:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height

        self.panel_height = 80
        self.panel_rect = pygame.Rect(0, self.sh - self.panel_height, self.sw, self.panel_height)

        self.bg_color = (35, 35, 40)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.active_color = (0, 255, 0)
        self.inactive_color = (80, 80, 80)

        self.current_team = 1
        self.selected_spawn_class = "Tank"

        self.font = pygame.font.SysFont("Courier", 14)

        self.btn_player = pygame.Rect(20, self.sh - 60, 120, 40)
        self.btn_enemy = pygame.Rect(150, self.sh - 60, 120, 40)
        self.btn_tank = pygame.Rect(320, self.sh - 60, 100, 40)
        self.btn_bmp = pygame.Rect(430, self.sh - 60, 100, 40)

    def handle_click(self, mouse_pos):
        if not self.panel_rect.collidepoint(mouse_pos):
            return False

        if self.btn_player.collidepoint(mouse_pos):
            self.current_team = 1
        elif self.btn_enemy.collidepoint(mouse_pos):
            self.current_team = 2
        elif self.btn_tank.collidepoint(mouse_pos):
            self.selected_spawn_class = "Tank"
        elif self.btn_bmp.collidepoint(mouse_pos):
            self.selected_spawn_class = "BMP"

        return True

    def draw_panel(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.panel_rect)
        pygame.draw.line(surface, self.border_color, (0, self.panel_rect.top), (self.sw, self.panel_rect.top), 2)

        color = self.active_color if self.current_team == 1 else self.inactive_color
        pygame.draw.rect(surface, color, self.btn_player, 1)
        txt = self.font.render("1. СОЮЗНИКИ", True, self.text_color if self.current_team == 1 else self.border_color)
        surface.blit(txt, (self.btn_player.x + 10, self.btn_player.y + 12))

        color = (255, 0, 0) if self.current_team == 2 else self.inactive_color
        pygame.draw.rect(surface, color, self.btn_enemy, 1)
        txt = self.font.render("2. ВОРОГИ", True, self.text_color if self.current_team == 2 else self.border_color)
        surface.blit(txt, (self.btn_enemy.x + 25, self.btn_enemy.y + 12))

        pygame.draw.line(surface, self.inactive_color, (295, self.panel_rect.top + 10), (295, self.sh - 10), 1)

        color = self.active_color if self.selected_spawn_class == "Tank" else self.inactive_color
        pygame.draw.rect(surface, color, self.btn_tank, 1)
        txt = self.font.render("СПАВН: ТАНК", True,
                               self.text_color if self.selected_spawn_class == "Tank" else self.border_color)
        surface.blit(txt, (self.btn_tank.x + 6, self.btn_tank.y + 12))

        color = self.active_color if self.selected_spawn_class == "BMP" else self.inactive_color
        pygame.draw.rect(surface, color, self.btn_bmp, 1)
        txt = self.font.render("СПАВН: БМП", True,
                               self.text_color if self.selected_spawn_class == "BMP" else self.border_color)
        surface.blit(txt, (self.btn_bmp.x + 10, self.btn_bmp.y + 12))

        inst_txt = self.font.render("[Зажми пробіл + Клік ЛКМ для спавна на полі]", True, (150, 150, 150))
        surface.blit(inst_txt, (self.sw - 380, self.sh - 45))

    def draw_hover_tooltip(self, surface, mouse_pos, hovered_unit):
        """Отрисовка всплывающей подсказки при наведении на юнита."""
        if not hovered_unit or self.panel_rect.collidepoint(mouse_pos):
            return

        team_text = "СОЮЗНИК" if hovered_unit.team == 1 else "ВРАГ"
        team_color = (100, 255, 100) if hovered_unit.team == 1 else (255, 100, 100)

        text_name = self.font.render(f"Имя: {hovered_unit.name} ({team_text})", True, team_color)
        text_type = self.font.render(f"Класс: {hovered_unit.unit_type} | HP: {hovered_unit.hp}/{hovered_unit.max_hp}",
                                     True, self.text_color)

        mx, my = mouse_pos
        bg_rect = pygame.Rect(mx + 15, my + 15, 250, 45)

        pygame.draw.rect(surface, (30, 30, 30), bg_rect)
        pygame.draw.rect(surface, team_color, bg_rect, 1)
        surface.blit(text_name, (mx + 20, my + 20))
        surface.blit(text_type, (mx + 20, my + 35))
