
import sys
import random
import pygame

# ════════════════════════════════
#          НАЛАШТУВАННЯ
# ════════════════════════════════
W, H = 820, 610
FPS = 60

SYMBOLS = [
    ("BUL", (220, 40, 40), 10),
    ("7", (210, 175, 25), 6),
    ("BAR", (70, 160, 230), 4),
    ("SHT", (220, 200, 50), 3),
    ("FUR", (200, 60, 100), 2),
]

N_REELS = 3
ROWS = 3
CELL_W = 140
CELL_H = 100
GAP = 18
REELS_W = N_REELS * CELL_W + (N_REELS - 1) * GAP
REELS_X = W // 2 - REELS_W // 2  # 182
REELS_Y = 95
REELS_H = ROWS * CELL_H  # 300

STOP_AT = [55, 85, 115]
SPIN_END = 140

# Кольори
C_BG = (15, 10, 25)
C_REEL_BG = (28, 20, 44)
C_REEL_BDR = (85, 65, 125)
C_WHITE = (255, 255, 255)
C_YELLOW = (230, 200, 30)
C_GOLD = (210, 175, 25)
C_GRAY = (120, 120, 120)
C_GREEN = (40, 190, 65)
C_RED = (200, 40, 40)
C_BLACK = (0, 0, 0)
C_DIM = (50, 40, 70)


# ═════════════════════════════
#         КЛАС БАРАБАНА
# ═════════════════════════════
class Reel:
    """
    Один барабан слот-машини.
    Зберігає 3 видимі символи (рядки).
    """
    ANIM_EVERY = 4

    def __init__(self):
        self.shown = [random.randrange(len(SYMBOLS)) for _ in range(ROWS)]
        self.spinning = False
        self._target = []
        self._tick = 0

    def start(self, target: list):
        self._target = target[:]
        self.spinning = True
        self._tick = 0

    def update(self, stop: bool):
        if not self.spinning:
            return
        if stop:
            self.shown = self._target[:]
            self.spinning = False
        else:
            self._tick += 1
            if self._tick >= self.ANIM_EVERY:
                self._tick = 0
                self.shown = [random.randrange(len(SYMBOLS)) for _ in range(ROWS)]

    def draw(self, surf: pygame.Surface, x: int, y: int,
             font_big: pygame.font.Font, font_sm: pygame.font.Font,
             highlight_row: int = 1, win: bool = False):
        rect = pygame.Rect(x, y, CELL_W, REELS_H)
        pygame.draw.rect(surf, C_REEL_BG, rect)
        pygame.draw.rect(surf, C_REEL_BDR, rect, 2)

        for row, sym_idx in enumerate(self.shown):
            label, color, _ = SYMBOLS[sym_idx]
            cy = y + row * CELL_H + CELL_H // 2

            if row == highlight_row:
                hi_col = (38, 72, 38) if win else (50, 42, 70)
                hi_rect = pygame.Rect(x + 2, y + row * CELL_H + 2, CELL_W - 4, CELL_H - 4)
                pygame.draw.rect(surf, hi_col, hi_rect)
                if win:
                    pygame.draw.rect(surf, C_GREEN, hi_rect, 3)

            txt = font_big.render(label, True, color)
            surf.blit(txt, (x + CELL_W // 2 - txt.get_width() // 2,
                            cy - txt.get_height() // 2))

            if row < ROWS - 1:
                ly = y + (row + 1) * CELL_H
                pygame.draw.line(surf, C_REEL_BDR, (x, ly), (x + CELL_W, ly), 1)


# ═══════════════════════════════════════════
#     КЛАС СЛОТ-МАШИНИ (З ГОЛОВНИМ МЕНЮ)
# ═══════════════════════════════════════════

class КазіноUA:
    """
    Управляє станом гри:
      'menu'     — головне меню (очікування старту)
      'idle'     — чекає натискання Spin
      'spinning' — барабани крутяться
      'result'   — показує результат, чекає наступного ходу
    """
    PAYLINE_ROW = 1

    def __init__(self, surf: pygame.Surface, fonts: dict):
        self.surf = surf
        self.fonts = fonts

        self.balance = 500
        self.bet = 25
        self.state = "menu"
        self.frame = 0
        self.message = ""
        self.win_amt = 0

        self.reels = [Reel() for _ in range(N_REELS)]
        self._results = []
        self.win_reels = []

        # Зони кнопок для гри
        self._btn_spin = pygame.Rect(W // 2 - 90, REELS_Y + REELS_H + 32, 180, 50)
        self._btn_bet_down = pygame.Rect(W // 2 - 155, REELS_Y + REELS_H + 100, 40, 36)
        self._btn_bet_up = pygame.Rect(W // 2 + 115, REELS_Y + REELS_H + 100, 40, 36)

        # Кнопки для головного меню
        self._btn_start = pygame.Rect(W // 2 - 120, H // 2 - 25, 240, 60)
        self._btn_exit = pygame.Rect(W // 2 - 120, H // 2 + 60, 240, 60)

    # ── обробка кліку ──────────────────────────────────────────────────────────
    def handle_click(self, pos: tuple):
        if self.state == "menu":
            if self._btn_start.collidepoint(pos):
                self.state = "idle"
            elif self._btn_exit.collidepoint(pos):
                pygame.quit()
                sys.exit()

        elif self.state == "idle":
            if self._btn_spin.collidepoint(pos):
                self._start_spin()
            elif self._btn_bet_up.collidepoint(pos):
                self.bet = min(100, self.bet + 25)
            elif self._btn_bet_down.collidepoint(pos):
                self.bet = max(25, self.bet - 25)

        elif self.state == "result":
            if self._btn_spin.collidepoint(pos):
                self.state = "idle"
                self.message = ""
                self.win_amt = 0
                self.win_reels = []

    # ── старт оберту ──────────────────────────────────────────────────────────
    def _start_spin(self):
        if self.balance < self.bet:
            self.message = "Недостатньо балансу!"
            return
        self.balance -= self.bet
        self.frame = 0
        self.state = "spinning"
        self.message = ""
        self.win_reels = []

        self._results = [
            [random.randrange(len(SYMBOLS)) for _ in range(ROWS)]
            for _ in range(N_REELS)
        ]
        for reel, target in zip(self.reels, self._results):
            reel.start(target)

    # ── перевірка виграшу ─────────────────────────────────────────────────────
    def _check_win(self):
        payline = [self.reels[r].shown[self.PAYLINE_ROW] for r in range(N_REELS)]

        if payline[0] == payline[1] == payline[2]:
            _, _, mult = SYMBOLS[payline[0]]
            self.win_amt = self.bet * mult
            self.balance += self.win_amt
            self.message = f"ПЕРЕМОГА!  +{self.win_amt}"
            self.win_reels = [0, 1, 2]

        elif payline[0] == payline[1]:
            _, _, mult = SYMBOLS[payline[0]]
            self.win_amt = self.bet * max(1, mult // 3)
            self.balance += self.win_amt
            self.message = f"2 поспіль!  +{self.win_amt}"
            self.win_reels = [0, 1]

        elif payline[1] == payline[2]:
            _, _, mult = SYMBOLS[payline[1]]
            self.win_amt = self.bet * max(1, mult // 3)
            self.balance += self.win_amt
            self.message = f"2 поспіль!  +{self.win_amt}"
            self.win_reels = [1, 2]
        else:
            self.win_amt = 0
            self.win_reels = []
            self.message = "Не пощастило..."

    # ── update ────────────────────────────────────────────────────────────────
    def update(self):
        if self.state != "spinning":
            return
        self.frame += 1
        for i, reel in enumerate(self.reels):
            reel.update(stop=(self.frame >= STOP_AT[i]))
        if self.frame >= SPIN_END:
            self._check_win()
            self.state = "result"

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        self.surf.fill(C_BG)

        if self.state == "menu":
            self._draw_menu()
            return

        f_big = self.fonts["big"]
        f_med = self.fonts["med"]
        f_sm = self.fonts["sm"]

        # Заголовок
        title = f_big.render("казіноUA777", True, C_YELLOW)
        self.surf.blit(title, (W // 2 - title.get_width() // 2, 18))

        # Лінія виплати
        pl_y = REELS_Y + self.PAYLINE_ROW * CELL_H + CELL_H // 2
        pygame.draw.line(self.surf, C_GOLD, (REELS_X - 14, pl_y), (REELS_X + REELS_W + 14, pl_y), 2)
        lbl = f_sm.render("PAY", True, C_GOLD)
        self.surf.blit(lbl, (REELS_X - 14 - lbl.get_width() - 4, pl_y - lbl.get_height() // 2))
        self.surf.blit(lbl, (REELS_X + REELS_W + 18, pl_y - lbl.get_height() // 2))

        # Барабани
        for i, reel in enumerate(self.reels):
            rx = REELS_X + i * (CELL_W + GAP)
            is_win = i in self.win_reels
            reel.draw(self.surf, rx, REELS_Y, f_big, f_sm, self.PAYLINE_ROW, win=is_win)

        # Баланс
        bal = f_med.render(f"Баланс:  {self.balance}", True, C_WHITE)
        self.surf.blit(bal, (W // 2 - bal.get_width() // 2, REELS_Y + REELS_H + 4))

        # Кнопка SPIN
        spinning = (self.state == "spinning")
        btn_color = C_DIM if spinning else (35, 110, 40)
        pygame.draw.rect(self.surf, btn_color, self._btn_spin, border_radius=8)
        pygame.draw.rect(self.surf, C_WHITE, self._btn_spin, 2, border_radius=8)
        btn_lbl = "КРУТИТИ" if self.state != "result" else "ДАЛІ"
        bt = f_med.render(btn_lbl, True, C_WHITE)
        self.surf.blit(bt, (self._btn_spin.centerx - bt.get_width() // 2,
                            self._btn_spin.centery - bt.get_height() // 2))

        # Ставка
        bet_lbl = f_med.render(f"Ставка:  {self.bet}", True, C_YELLOW)
        self.surf.blit(bet_lbl, (W // 2 - bet_lbl.get_width() // 2, REELS_Y + REELS_H + 103))

        for btn, lbl_txt in [(self._btn_bet_down, "-"), (self._btn_bet_up, "+")]:
            active = (self.state == "idle")
            col = (45, 38, 68) if active else C_DIM
            pygame.draw.rect(self.surf, col, btn, border_radius=4)
            pygame.draw.rect(self.surf, C_GRAY, btn, 1, border_radius=4)
            t = f_med.render(lbl_txt, True, C_WHITE if active else C_GRAY)
            self.surf.blit(t, (btn.centerx - t.get_width() // 2, btn.centery - t.get_height() // 2))

        # Повідомлення про результат
        if self.message:
            col = C_GREEN if "ПЕРЕМОГА" in self.message else (C_YELLOW if "2 поспіль" in self.message else C_RED)
            msg = f_big.render(self.message, True, col)
            self.surf.blit(msg, (W // 2 - msg.get_width() // 2, REELS_Y + REELS_H + 150))

        # Таблиця виплат
        tx, ty = REELS_X + REELS_W + 30, REELS_Y
        hdr = f_sm.render("Виплати (x3):", True, C_GRAY)
        self.surf.blit(hdr, (tx, ty))
        ty += 22
        for label, color, mult in SYMBOLS:
            self.surf.blit(f_sm.render(f"  {label:<4}  x{mult}", True, color), (tx, ty))
            ty += 20

        ty += 10
        hdr2 = f_sm.render("2 поспіль:", True, C_GRAY)
        self.surf.blit(hdr2, (tx, ty))
        ty += 22
        for label, color, mult in SYMBOLS:
            partial = max(1, mult // 3)
            dim_col = tuple(max(0, c - 70) for c in color)
            self.surf.blit(f_sm.render(f"  {label:<4}  x{partial}", True, dim_col), (tx, ty))
            ty += 20

        hint = f_sm.render("Лінія виплати — середній рядок", True, C_GRAY)
        self.surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 24))

    # ── відмальовування меню ──────────────────────────────────────────────────
    def _draw_menu(self):
        f_big = self.fonts["big"]
        f_med = self.fonts["med"]
        f_sm = self.fonts["sm"]

        # Заголовки по центру
        title = f_big.render("ГОЛОВНЕ МЕНЮ", True, C_YELLOW)
        self.surf.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 100))

        subtitle = f_med.render("КазіноUA777", True, C_GOLD)
        self.surf.blit(subtitle, (W // 2 - subtitle.get_width() // 2, H // 2 - 140))

        # Кнопка СТАРТ
        pygame.draw.rect(self.surf, (35, 110, 40), self._btn_start, border_radius=10)
        pygame.draw.rect(self.surf, C_WHITE, self._btn_start, 2, border_radius=10)
        txt_start = f_med.render("ГРАТИ", True, C_WHITE)
        self.surf.blit(txt_start, (self._btn_start.centerx - txt_start.get_width() // 2,
                                   self._btn_start.centery - txt_start.get_height() // 2))

        # Кнопка ВИХІД
        pygame.draw.rect(self.surf, (140, 35, 35), self._btn_exit, border_radius=10)
        pygame.draw.rect(self.surf, C_WHITE, self._btn_exit, 2, border_radius=10)
        txt_exit = f_med.render("ВИХІД", True, C_WHITE)
        self.surf.blit(txt_exit, (self._btn_exit.centerx - txt_exit.get_width() // 2,
                                  self._btn_exit.centery - txt_exit.get_height() // 2))

        # Підказка знизу
        hint = f_sm.render("Управління: Пропуск / Мишка / Enter", True, C_GRAY)
        self.surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 40))


# ══════════════════════════════
#         ГОЛОВНИЙ ЦИКЛ
# ══════════════════════════════

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("КазіноUA777")
    clock = pygame.time.Clock()

    fonts = {
        "big": pygame.font.SysFont("consolas", 42, bold=True),
        "med": pygame.font.SysFont("consolas", 26),
        "sm": pygame.font.SysFont("consolas", 18),
    }

    game = КазіноUA(screen, fonts)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                game.handle_click(ev.pos)

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and game.state == "menu":
                    game.state = "idle"
                elif ev.key == pygame.K_SPACE and game.state == "idle":
                    game.handle_click(game._btn_spin.center)
                elif ev.key == pygame.K_RETURN and game.state == "result":
                    game.handle_click(game._btn_spin.center)

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()