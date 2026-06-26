import pygame
import sys
from units import Tank, BMP
from ui import SpawnMenu

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RTS")
clock = pygame.time.Clock()

BG_COLOR = (25, 30, 25)
TEXT_COLOR = (255, 255, 255)
UI_BG = (30, 30, 30)
MENU_BG = (15, 20, 15)
BTN_COLOR = (40, 60, 40)
BTN_HOVER = (60, 90, 60)

font = pygame.font.SysFont("Courier", 14)
font_large = pygame.font.SysFont("Courier", 24)

game_state = "MENU"

btn_play = pygame.Rect(400, 300, 200, 50)
btn_sandbox = pygame.Rect(400, 280, 200, 50)
btn_campaign = pygame.Rect(400, 360, 200, 50)
btn_popup_close = pygame.Rect(400, 400, 200, 40)

units = []
selected_units = []
bullets = []
ui_menu = SpawnMenu(WIDTH, HEIGHT)
selection_start = None
is_selecting = False


def start_sandbox():
    global units, selected_units, bullets, game_state
    bullets.clear()
    selected_units.clear()

    units = [
        Tank(150, 200, "Т-72", 1, (50, 150, 200)),
        Tank(150, 250, "Т-72", 1, (50, 150, 200)),
        BMP(120, 220, "БМП-2", 1, (100, 160, 100)),
        BMP(120, 270, "БМП-2", 1, (100, 160, 100)),
        Tank(700, 400, "M1 Abrams", 2, (200, 70, 70)),
        BMP(750, 430, "M2 Bradley", 2, (180, 100, 70)),
        BMP(750, 380, "M2 Bradley", 2, (180, 100, 70))
    ]
    game_state = "GAMEPLAY"


while True:
    mouse_pos = pygame.mouse.get_pos()
    hovered_unit = None
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play.collidepoint(mouse_pos):
                    game_state = "MODE_SELECT"

        elif game_state == "MODE_SELECT":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_sandbox.collidepoint(mouse_pos):
                    start_sandbox()
                elif btn_campaign.collidepoint(mouse_pos):
                    game_state = "CAMPAIGN_POPUP"

        elif game_state == "CAMPAIGN_POPUP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_popup_close.collidepoint(mouse_pos):
                    game_state = "MODE_SELECT"

        elif game_state == "GAMEPLAY":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ui_clicked = ui_menu.handle_click(mouse_pos)
                    if not ui_clicked:
                        if keys[pygame.K_SPACE]:
                            team = ui_menu.current_team
                            u_class = ui_menu.selected_spawn_class
                            if team == 1:
                                if u_class == "Tank":
                                    units.append(Tank(mouse_pos[0], mouse_pos[1], "Т-72", 1, (50, 150, 200)))
                                else:
                                    units.append(BMP(mouse_pos[0], mouse_pos[1], "БМП-2", 1, (100, 160, 100)))
                            else:
                                if u_class == "Tank":
                                    units.append(Tank(mouse_pos[0], mouse_pos[1], "M1 Abrams", 2, (200, 70, 70)))
                                else:
                                    units.append(BMP(mouse_pos[0], mouse_pos[1], "M2 Bradley", 2, (180, 100, 70)))
                        else:
                            selection_start = mouse_pos
                            is_selecting = True

                elif event.button == 3:
                    if not ui_menu.panel_rect.collidepoint(mouse_pos):
                        for u in selected_units:
                            u.target_pos = mouse_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_selecting:
                    is_selecting = False
                    end_pos = mouse_pos
                    x1, y1 = selection_start
                    x2, y2 = end_pos
                    select_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

                    if select_rect.width < 6 and select_rect.height < 6:
                        selected_units.clear()
                        for u in units:
                            if u.check_hover(end_pos) and u.team == 1:
                                selected_units.append(u)
                                break
                    else:
                        selected_units.clear()
                        for u in units:
                            if u.team == 1 and select_rect.colliderect(u.rect):
                                selected_units.append(u)

    if game_state == "MENU":
        screen.fill(MENU_BG)
        color = BTN_HOVER if btn_play.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, btn_play)
        pygame.draw.rect(screen, TEXT_COLOR, btn_play, 1)
        txt = font_large.render("ГРАТИ", True, TEXT_COLOR)
        screen.blit(txt, (btn_play.x + 65, btn_play.y + 12))

    elif game_state == "MODE_SELECT":
        screen.fill(MENU_BG)
        color = BTN_HOVER if btn_sandbox.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, btn_sandbox)
        pygame.draw.rect(screen, TEXT_COLOR, btn_sandbox, 1)
        txt1 = font_large.render("SANDBOX", True, TEXT_COLOR)
        screen.blit(txt1, (btn_sandbox.x + 50, btn_sandbox.y + 12))

        color = BTN_HOVER if btn_campaign.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, btn_campaign)
        pygame.draw.rect(screen, TEXT_COLOR, btn_campaign, 1)
        txt2 = font_large.render("КАМПАНІЯ", True, TEXT_COLOR)
        screen.blit(txt2, (btn_campaign.x + 45, btn_campaign.y + 12))

    elif game_state == "CAMPAIGN_POPUP":
        screen.fill(MENU_BG)
        popup_rect = pygame.Rect(250, 200, 500, 300)
        pygame.draw.rect(screen, UI_BG, popup_rect)
        pygame.draw.rect(screen, (255, 0, 0), popup_rect, 2)

        txt = font_large.render("Техно-демка, буде доступно пізніше", True, TEXT_COLOR)
        screen.blit(txt, (300, 280))

        color = BTN_HOVER if btn_popup_close.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, btn_popup_close)
        pygame.draw.rect(screen, TEXT_COLOR, btn_popup_close, 1)
        txt_ok = font_large.render("OK", True, TEXT_COLOR)
        screen.blit(txt_ok, (btn_popup_close.x + 85, btn_popup_close.y + 8))

    elif game_state == "GAMEPLAY":
        units = [u for u in units if u.hp > 0]
        selected_units = [u for u in selected_units if u.hp > 0]

        for u in units:
            u.update(units, bullets)
            if u.check_hover(mouse_pos):
                hovered_unit = u

        for b in bullets:
            b.update()
        bullets = [b for b in bullets if b.active]

        screen.fill(BG_COLOR)

        for b in bullets:
            b.draw(screen)
        for u in units:
            u.draw(screen, is_selected=(u in selected_units))

        if is_selecting:
            x1, y1 = selection_start
            x2, y2 = mouse_pos
            current_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            pygame.draw.rect(screen, (0, 255, 0), current_rect, 1)

        ui_menu.draw_panel(screen)
        ui_menu.draw_hover_tooltip(screen, mouse_pos, hovered_unit)

    pygame.display.flip()
    clock.tick(60)
