import pygame
import sys
from backend import PuzzleSolver

# importo librarias para crear la interfaz gráfica, leer eventos de teclado/raton, etc con pygame.
# tambien pues importo la clase PuzzleSolver del backend para usar sus métodos y atributos, que resuelve el puzzle con A*.

#NUEVA VERSION

class PuzzleUI:
    def __init__(self):
        # Inicializo pygame y variables
        pygame.init()

        # y defino dimensiones, tablero 300x300 (3x3 celdas de 100x100)
        self.board_size = 300
        self.tile_size = self.board_size // 3

        # Panel lateral (instrucciones) a la izquierda
        self.panel_width = 200

        # tablero + (zona sur) (botones/paleta/campo meta)
        self.height = self.board_size + 300   
        self.width = self.board_size + self.panel_width


        # creo la ventana de pygame, y en el se dibujará todo
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Título ventana (8 Puzzle)
        pygame.display.set_caption("8 Puzzle")


        # Defino 3 Fuentes para textos
        self.font  = pygame.font.Font(None, 28)
        self.big   = pygame.font.Font(None, 50)
        self.small = pygame.font.Font(None, 22)


        # reao la instancia de la Puzzlesolver de la clase backend y estado inicial/meta
        self.solver = PuzzleSolver()

        # defino el estado inicial del tablero 3x3 en 0s (vacío)
        # para que el usuario lo edite
        # el 0 representa la celda vacía
        self.state = [[0,0,0],[0,0,0],[0,0,0]]

        # aqui defino el estado meta por defecto (que lo puede cambiar el usuario)
        self.solver.set_goal_state([[1,2,3],[4,5,6],[7,8,0]])



        # Variables de estado de la interfaz gráfica
        # entonces aguarda si estoy "start"= editando estado inicial, "goal"= editando meta, o None=ninguno
        self.edit_mode = None  # "start" | "goal" | None
        self.selected_tile = None
        self.message = ""

        # Coordenadas base
        # el tablero va en la esquina superior derecha
        self.board_x = self.panel_width
        south_top = self.board_size  # y base del área sur


        # utilizo la funcion rect de pygame para dibujar botones y zonas clicables
        # creo 4 Botones (en el sur, bajo el tablero)
        self.buttons = {
            "edit_start": pygame.Rect(self.board_x + 10,  south_top + 20, 120, 38),
            "edit_goal":  pygame.Rect(self.board_x + 140, south_top + 20, 120, 38),
            "solve":      pygame.Rect(self.board_x + 10,  south_top + 70, 120, 38),
            "clear":      pygame.Rect(self.board_x + 140, south_top + 70, 120, 38),
        }


        # despues creo la paleta de números 0–8 (botones) para editar el inicio
        # Paleta 0–8 EN EL SUR (centrada bajo los botones)
        # La dibujaremos/activaremos solo en modo "start"

        # cada boton mide 36px, son 3 columnas, y hay 12px de espacio entre ellos
        grid_w = 3 * 36 + 2 * 12   # ancho aprox de 3 celdas + separaciones

        # coordenadas inicio de la paleta (centrada horizontalmente)
        # para que quede centrada en el sur
        start_x = self.board_x + (self.board_size - grid_w) // 2

        # se ubica 120px bajo los botones principales (editarInicio, EditarMeta, Resolver, Limpiar)
        start_y = south_top + 120
        
        # creo los rectangulos de cada boton numerico (0-8)
        self.num_buttons = []
        k = 0
        for r in range(3): # 3 filas
            for c in range(3): # 3 columnas
                self.num_buttons.append(
                    pygame.Rect(start_x + c*48, start_y + r*48, 36, 36)  # 36x36px cada boton,  (36+12)= 48px (12 de separacion) 
                )
                k += 1

        # Campo de texto para meta (cuando editas meta) — también en el sur
        # campo de texto para que el usuario escriba la meta cuando esta en modo editar meta
        # lo ubicamos bajo los botones principales 
        self.goal_input_rect = pygame.Rect(self.board_x + 10, south_top + 120, 250, 34)
        self.goal_input_text = "" # aqui aguarda lo que el usuario escribe
        self._refresh_goal_placeholder() # llama a un metodo que genera un texto

        # Instrucciones (panel oeste)
        self.instructions = (
            "• EDITAR INICIO: clic en casilla del tablero y elige número (0 = vacío). "
            "Usa cada número 0–8 una vez.\n\n"
            "• EDITAR META: escribe los 9 dígitos (0–8) y pulsa Enter.\n\n"
            "• RESOLVER: ejecuta hacia la meta.\n\n"
            "• LIMPIAR: reinicia el tablero inicial."
        )


    # aqui se define el texto que aparece en el campo de texto cuando el usuario no ha escrito nada
    def _refresh_goal_placeholder(self):
        flat = [n for row in self.solver.goal_state for n in row]
        self.goal_placeholder = " ".join(str(x) for x in flat)

    # ---------- Dibujo ----------
    def draw(self):

        # Fondo blanco
        self.screen.fill((255, 255, 255))

        # Panel para las instrucciones (oeste)
        pygame.draw.rect(self.screen, (245,245,245), (0,0,self.panel_width,self.height))    # fondo gris claro
        pygame.draw.rect(self.screen, (200,200,200), (0,0,self.panel_width,self.height), 1) # borde gris
        title = self.font.render("Instrucciones", True, (0,0,0)) # titulo de instrucciones
        self.screen.blit(title, (10, 10)) # lo dibujo en la esquina superior izquierda del panel
        text_rect = pygame.Rect(10, 50, self.panel_width-20, self.height-60) # area para el texto de instrucciones
        self._blit_wrapped_text(self.small, self.instructions, (40,40,40), text_rect, line_spacing=3) # llamo a un metodo que dibuja el texto con saltos de linea y ajuste automatico

        # Tablero (arriba a la derecha)
        for i in range(3): # filas
            for j in range(3):# columnas
                value = self.state[i][j] # obtiene el valor de la celda
                # crea el cuadrado que representa la celda en la pantalla
                rect = pygame.Rect(self.board_x + j*self.tile_size, i*self.tile_size,
                                   self.tile_size, self.tile_size)
                

                # si la celda esta seleccionada, la resalta en azul, sino gris claro
                pygame.draw.rect(self.screen, (0,128,255) if value != 0 else (200,200,200), rect)
                
                
                if value != 0:
                    text = self.big.render(str(value), True, (255,255,255)) # convierte el numero a texto grande blanco
                    self.screen.blit(text, text.get_rect(center=rect.center)) # lo dibuja centrado en la celda
                pygame.draw.rect(self.screen, (0,0,0), rect, 2) # dibuja una linea negra alrededor de la celda para separar

        # Botones (sur) con sus etiquetas
        labels = {
            "edit_start":"Editar Inicio",
            "edit_goal":"Editar Meta",
            "solve":"Resolver",
            "clear":"Limpiar"
        }
        for key, rect in self.buttons.items(): # recorre los botones, key es el nombre, rect es el rectangulo definido antes

            active = (key == "edit_start" and self.edit_mode == "start") or \
                     (key == "edit_goal"  and self.edit_mode == "goal") # determina si el boton esta activo (modo edicion inicio o editar meta) para que cambien de color si estan activos
            bg = (200,230,255) if active else (220,220,220) # si esta activo lo declare azul claro, sino gris claro
            pygame.draw.rect(self.screen, bg, rect, border_radius=6) # dibuja el boton
            
            # lo que hace es que el texto del boton se centre en el rectangulo del boton
            tw = self.font.render(labels[key], True, (0,0,0)) 
            self.screen.blit(tw, (rect.x+(rect.w-tw.get_width())//2,
                                  rect.y+(rect.h-tw.get_height())//2))

        # Zona sur dinámica:
        # - Si editando INICIO: mostrar paleta 0–8 centrada en el sur.
        #   Si no hay celda seleccionada, la paleta aparece deshabilitada (gris claro).
        
            # verifica si estoy en modo editar inicio, cuando estoy armando la paleta numerica
        if self.edit_mode == "start":
            used = self._used_numbers(matrix=self.state, exclude=self.selected_tile) if self.selected_tile else set() # verifico que el numero no este ya usado en el tablero
            
            # en el for se dibujan los botones numericos
            for i, rect in enumerate(self.num_buttons):
                if self.selected_tile is None:
                    # deshabilitado si no hay celda seleccionada
                    color_fill = (235,235,235)
                    color_text = (170,170,170)
                else:
                    disabled = (i in used) # deshabilitado si el numero ya esta en uso en el tablero
                    color_fill = (180,180,180) if not disabled else (230,230,230) # gris oscuro si habilitado, gris claro si deshabilitado
                    color_text = (0,0,0) if not disabled else (150,150,150) # si ya esta en uso, texto gris claro
                    # aparece bloqueado si el numero ya esta en uso en el tablero


                # esto hace que cada numero se dibuje en su boton correspondiente
                pygame.draw.rect(self.screen, color_fill, rect, border_radius=6)
                pygame.draw.rect(self.screen, (120,120,120), rect, 1, border_radius=6)
                t = self.font.render(str(i), True, color_text) # convierte el numero a texto y muestra en el boton en el centro
                self.screen.blit(t, t.get_rect(center=rect.center))

        # - Si editando META: mostrar campo de texto (en el sur), el jugador escribe la meta
        if self.edit_mode == "goal":
            pygame.draw.rect(self.screen, (255,255,255), self.goal_input_rect, border_radius=6) # dibuja un rectangulo blanco para el campo de texto
            pygame.draw.rect(self.screen, (120,120,120), self.goal_input_rect, 1, border_radius=6) # borde gris
            txt = self.goal_input_text if self.goal_input_text else self.goal_placeholder # si el usuario no ha escrito nada, muestra el texto de ayuda, y si escribe, muestra lo que escribe
            color = (0,0,0) if self.goal_input_text else (150,150,150)

            # ahora el campo se ve como un rectangulo con el texto dentro
            surf = self.font.render(txt, True, color)
            self.screen.blit(surf, (self.goal_input_rect.x+8, self.goal_input_rect.y+6))

            # y un pequeño hint debajo para ayudar al usuario
            hint = self.small.render("Enter = aplicar meta", True, (80,80,80)) 
            self.screen.blit(hint, (self.goal_input_rect.x, self.goal_input_rect.y+40))

        # Mensaje (ej: ganador/errores)
        # si hay un mensaje (ganador, error, etc) lo muestra en la parte inferior del tablero
        if self.message:
            color = (0,120,0) if self.message == "ganador" else (200,0,0)
            msg = self.font.render(self.message, True, color)
            self.screen.blit(msg, (self.board_x-100, self.board_size+200))

        pygame.display.flip()




    # Dibuja texto con saltos de línea y ajuste automático de las instrucciones
    def _blit_wrapped_text(self, font, text, color, rect, line_spacing=0):
        words = [w for line in text.splitlines() for w in (line.split(' ') + ['\n'])] # convierte el texto en una lista de palabras, manteniendo los saltos de linea para que se vea bonito
        
        # empieza a escribir en la esquina izquierda
        x, y = rect.topleft
        line = ""


        # recorre cada palabra y la añade a la línea actual si cabe, sino dibuja la línea y empieza una nueva
        for word in words:
            if word == '\n':
                if line:
                    surf = font.render(line, True, color); self.screen.blit(surf, (x, y))
                    y += surf.get_height() + line_spacing; line = ""
                else:
                    y += font.get_height() + line_spacing
                continue

            # prueba si la palabra cabe en la línea actual, si cabe la añade, sino dibuja la línea y empieza una nueva
            test = (line + (" " if line else "") + word)
            if font.size(test)[0] <= rect.width:
                line = test
            else:
                surf = font.render(line, True, color); self.screen.blit(surf, (x, y))
                y += surf.get_height() + line_spacing; line = word
            
            # si el texto se sale del rectangulo, no lo dibuja
            if y > rect.bottom - font.get_height():
                break
        
        # si al terminar queda texto en la línea, lo dibuja
        if line and y <= rect.bottom:
            surf = font.render(line, True, color); self.screen.blit(surf, (x, y))

    # ---------- Utilidades ----------

    # devuelve los numeros ya usados en la matriz
    def _used_numbers(self, matrix, exclude=None):
        used = set() # aqui se guardan los numeros ya usados
        ex_val = None # valor de la celda excluida (si hay)
        if exclude is not None: # si no es none, entonces el usuario selecciono una casilla para editar
            r, c = exclude # fila y columna de la celda seleccionada
            ex_val = matrix[r][c] # guarda el numero que estaba en esa celda
        
        #recorre toda la matriz
        # si i,j es la celda excluida se salta, si no añade el numero de esa celda al conjunto de usados
        for i in range(3):
            for j in range(3):
                if exclude and (i,j) == exclude:
                    continue
                used.add(matrix[i][j])

                # mmm en el caso de que pase que el valor de la celda excluida ya estuviera en uso, lo eliminamos
        if ex_val in used:
            used.remove(ex_val)
        return used



    # verifica si el estado inicial y la meta son válidos (contienen los números 0-8 sin repetir)
    # sirve como filtro antes de intentar resolver el puzzle, evitando que el algoritmo trabaje con datos/estados inválidos
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
        # Botón Editar Inicio
        if self.buttons["edit_start"].collidepoint(pos):
            self.edit_mode = "start" if self.edit_mode != "start" else None
            self.selected_tile = None
            return
        
        # Botón Editar Meta
        if self.buttons["edit_goal"].collidepoint(pos):
            self.edit_mode = "goal" if self.edit_mode != "goal" else None
            self.selected_tile = None
            return
        # Botón Limpiar
        # elimina todo el estado inicial, mensaje, modo edicion y celda seleccionada
        if self.buttons["clear"].collidepoint(pos):
            self.state = [[0,0,0],[0,0,0],[0,0,0]]
            self.message = ""
            self.edit_mode = None
            self.selected_tile = None
            return
        
        # Botón Resolver
        if self.buttons["solve"].collidepoint(pos):
            if not self._both_valid(): # confirma que el estado inicial y la meta son válidos
                self.message = "Estado/meta inválidos"; return
            if not self.solver.is_solvable(self.state, self.solver.goal_state): # confirma que el puzzle es resolvible
                self.message = "Insoluble"; return
            path = self.solver.a_star(self.state) # si todo esta bien, comienza a resolver con A*
            if not path: self.message = "Sin solución"; return # si no hay camino, mensaje de error
            for st in path:
                self.state = st; self.draw(); pygame.time.delay(220)
            self.message = "ganador"; self.edit_mode = None; self.selected_tile = None; return # al final muestra mensaje ganador

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
