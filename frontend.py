import pygame
import sys
from backend import PuzzleSolver

#NUEVA VERSION

class PuzzleUI:
    def __init__(self):
        pygame.init()
        self.board_size = 300
        self.tile_size = self.board_size // 3

        # Panel lateral (instrucciones) a la izquierda
        self.panel_width = 200
        self.height = self.board_size + 300   # tablero + zona sur (botones/paleta/campo meta)
        self.width = self.board_size + self.panel_width

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.setCaption = pygame.display.set_caption("8 Puzzle")

        self.font  = pygame.font.Font(None, 28)
        self.big   = pygame.font.Font(None, 50)
        self.small = pygame.font.Font(None, 22)

        self.solver = PuzzleSolver()
        self.state = [[0,0,0],[0,0,0],[0,0,0]]
        self.solver.set_goal_state([[1,2,3],[4,5,6],[7,8,0]])

        self.edit_mode = None  # "start" | "goal" | None
        self.selected_tile = None
        self.message = ""

        # Coordenadas base
        self.board_x = self.panel_width
        south_top = self.board_size  # y base del área sur

        # Botones (en el sur, bajo el tablero)
        self.buttons = {
            "edit_start": pygame.Rect(self.board_x + 10,  south_top + 20, 120, 38),
            "edit_goal":  pygame.Rect(self.board_x + 140, south_top + 20, 120, 38),
            "solve":      pygame.Rect(self.board_x + 10,  south_top + 70, 120, 38),
            "clear":      pygame.Rect(self.board_x + 140, south_top + 70, 120, 38),
        }

        # Paleta 0–8 EN EL SUR (centrada bajo los botones)
        # La dibujaremos/activaremos solo en modo "start"
        grid_w = 3 * 36 + 2 * 12   # ancho aprox de 3 celdas + separaciones
        start_x = self.board_x + (self.board_size - grid_w) // 2
        start_y = south_top + 120
        self.num_buttons = []
        k = 0
        for r in range(3):
            for c in range(3):
                self.num_buttons.append(
                    pygame.Rect(start_x + c*48, start_y + r*48, 36, 36)
                )
                k += 1

        # Campo de texto para meta (cuando editas meta) — también en el sur
        self.goal_input_rect = pygame.Rect(self.board_x + 10, south_top + 120, 250, 34)
        self.goal_input_text = ""
        self._refresh_goal_placeholder()

        # Instrucciones (panel oeste)
        self.instructions = (
            "• EDITAR INICIO: clic en casilla del tablero y elige número (0 = vacío). "
            "Usa cada número 0–8 una vez.\n\n"
            "• EDITAR META: escribe los 9 dígitos (0–8) y pulsa Enter.\n\n"
            "• RESOLVER: ejecuta hacia la meta.\n\n"
            "• LIMPIAR: reinicia el tablero inicial."
        )

    def _refresh_goal_placeholder(self):
        flat = [n for row in self.solver.goal_state for n in row]
        self.goal_placeholder = " ".join(str(x) for x in flat)

    # ---------- Dibujo ----------
    def draw(self):
        self.screen.fill((255, 255, 255))

        # Panel instrucciones (oeste)
        pygame.draw.rect(self.screen, (245,245,245), (0,0,self.panel_width,self.height))
        pygame.draw.rect(self.screen, (200,200,200), (0,0,self.panel_width,self.height), 1)
        title = self.font.render("Instrucciones", True, (0,0,0))
        self.screen.blit(title, (10, 10))
        text_rect = pygame.Rect(10, 50, self.panel_width-20, self.height-60)
        self._blit_wrapped_text(self.small, self.instructions, (40,40,40), text_rect, line_spacing=3)

        # Tablero (arriba a la derecha)
        for i in range(3):
            for j in range(3):
                value = self.state[i][j]
                rect = pygame.Rect(self.board_x + j*self.tile_size, i*self.tile_size,
                                   self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, (0,128,255) if value != 0 else (200,200,200), rect)
                if value != 0:
                    text = self.big.render(str(value), True, (255,255,255))
                    self.screen.blit(text, text.get_rect(center=rect.center))
                pygame.draw.rect(self.screen, (0,0,0), rect, 2)

        # Botones (sur)
        labels = {
            "edit_start":"Editar Inicio",
            "edit_goal":"Editar Meta",
            "solve":"Resolver",
            "clear":"Limpiar"
        }
        for key, rect in self.buttons.items():
            active = (key == "edit_start" and self.edit_mode == "start") or \
                     (key == "edit_goal"  and self.edit_mode == "goal")
            bg = (200,230,255) if active else (220,220,220)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            tw = self.font.render(labels[key], True, (0,0,0))
            self.screen.blit(tw, (rect.x+(rect.w-tw.get_width())//2,
                                  rect.y+(rect.h-tw.get_height())//2))

        # Zona sur dinámica:
        # - Si editando INICIO: mostrar paleta 0–8 centrada en el sur.
        #   Si no hay celda seleccionada, la paleta aparece deshabilitada (gris claro).
        if self.edit_mode == "start":
            used = self._used_numbers(matrix=self.state, exclude=self.selected_tile) if self.selected_tile else set()
            for i, rect in enumerate(self.num_buttons):
                if self.selected_tile is None:
                    # deshabilitado si no hay celda seleccionada
                    color_fill = (235,235,235)
                    color_text = (170,170,170)
                else:
                    disabled = (i in used)
                    color_fill = (180,180,180) if not disabled else (230,230,230)
                    color_text = (0,0,0) if not disabled else (150,150,150)
                pygame.draw.rect(self.screen, color_fill, rect, border_radius=6)
                pygame.draw.rect(self.screen, (120,120,120), rect, 1, border_radius=6)
                t = self.font.render(str(i), True, color_text)
                self.screen.blit(t, t.get_rect(center=rect.center))

        # - Si editando META: mostrar campo de texto (en el sur)
        if self.edit_mode == "goal":
            pygame.draw.rect(self.screen, (255,255,255), self.goal_input_rect, border_radius=6)
            pygame.draw.rect(self.screen, (120,120,120), self.goal_input_rect, 1, border_radius=6)
            txt = self.goal_input_text if self.goal_input_text else self.goal_placeholder
            color = (0,0,0) if self.goal_input_text else (150,150,150)
            surf = self.font.render(txt, True, color)
            self.screen.blit(surf, (self.goal_input_rect.x+8, self.goal_input_rect.y+6))
            hint = self.small.render("Enter = aplicar meta", True, (80,80,80))
            self.screen.blit(hint, (self.goal_input_rect.x, self.goal_input_rect.y+40))

        # Mensaje (ej: ganador/errores)
        if self.message:
            color = (0,120,0) if self.message == "ganador" else (200,0,0)
            msg = self.font.render(self.message, True, color)
            self.screen.blit(msg, (self.board_x-100, self.board_size+200))

        pygame.display.flip()

    def _blit_wrapped_text(self, font, text, color, rect, line_spacing=0):
        words = [w for line in text.splitlines() for w in (line.split(' ') + ['\n'])]
        x, y = rect.topleft
        line = ""
        for word in words:
            if word == '\n':
                if line:
                    surf = font.render(line, True, color); self.screen.blit(surf, (x, y))
                    y += surf.get_height() + line_spacing; line = ""
                else:
                    y += font.get_height() + line_spacing
                continue
            test = (line + (" " if line else "") + word)
            if font.size(test)[0] <= rect.width:
                line = test
            else:
                surf = font.render(line, True, color); self.screen.blit(surf, (x, y))
                y += surf.get_height() + line_spacing; line = word
            if y > rect.bottom - font.get_height():
                break
        if line and y <= rect.bottom:
            surf = font.render(line, True, color); self.screen.blit(surf, (x, y))

    # ---------- Utilidades ----------
    def _used_numbers(self, matrix, exclude=None):
        used = set()
        ex_val = None
        if exclude is not None:
            r, c = exclude
            ex_val = matrix[r][c]
        for i in range(3):
            for j in range(3):
                if exclude and (i,j) == exclude:
                    continue
                used.add(matrix[i][j])
        if ex_val in used:
            used.remove(ex_val)
        return used

    def _both_valid(self):
        try:
            return self.solver.is_valid(self.state) and self.solver.is_valid(self.solver.goal_state)
        except Exception:
            return False

    # ---------- Interacción ----------
    def handle_click(self, pos):
        x, y = pos

        # Tablero (solo en Editar Inicio)
        if x >= self.panel_width and y < self.board_size and self.edit_mode == "start":
            col = (x - self.board_x) // self.tile_size
            row = y // self.tile_size
            self.selected_tile = (row, col)
            self.message = ""
            return

        # Botones
        if self.buttons["edit_start"].collidepoint(pos):
            self.edit_mode = "start" if self.edit_mode != "start" else None
            self.selected_tile = None
            return
        if self.buttons["edit_goal"].collidepoint(pos):
            self.edit_mode = "goal" if self.edit_mode != "goal" else None
            self.selected_tile = None
            return
        if self.buttons["clear"].collidepoint(pos):
            self.state = [[0,0,0],[0,0,0],[0,0,0]]
            self.message = ""
            self.edit_mode = None
            self.selected_tile = None
            return
        if self.buttons["solve"].collidepoint(pos):
            if not self._both_valid():
                self.message = "Estado/meta inválidos"; return
            if not self.solver.is_solvable(self.state, self.solver.goal_state):
                self.message = "Insoluble"; return
            path = self.solver.a_star(self.state)
            if not path: self.message = "Sin solución"; return
            for st in path:
                self.state = st; self.draw(); pygame.time.delay(220)
            self.message = "ganador"; self.edit_mode = None; self.selected_tile = None; return

        # Paleta en el SUR (solo si modo start). Requiere celda seleccionada.
        if self.edit_mode == "start" and self.selected_tile is not None:
            used = self._used_numbers(matrix=self.state, exclude=self.selected_tile)
            for i, rect in enumerate(self.num_buttons):
                if rect.collidepoint(pos):
                    if i in used:
                        return
                    r, c = self.selected_tile
                    self.state[r][c] = i
                    self.selected_tile = None
                    return

    def handle_keydown(self, event):
        if self.edit_mode != "goal":
            return
        if event.key == pygame.K_RETURN:
            digits = [int(ch) for ch in self.goal_input_text if ch.isdigit()]
            if len(digits) == 9 and sorted(digits) == list(range(9)):
                new_goal = [digits[i*3:(i+1)*3] for i in range(3)]
                self.solver.set_goal_state(new_goal)
                self._refresh_goal_placeholder()
                self.message = "Meta actualizada"; self.goal_input_text = ""
            else:
                self.message = "Meta inválida"; return
        elif event.key == pygame.K_BACKSPACE:
            self.goal_input_text = self.goal_input_text[:-1]
        else:
            ch = event.unicode
            if ch.isdigit() or ch in " ,;.-":
                self.goal_input_text += ch

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN: self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN: self.handle_keydown(event)
            clock.tick(60)
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    ui = PuzzleUI()
    ui.run()
