# Exemplos Avançados - BitDogLab V7 Framework

Coleção de exemplos práticos para inspirar seus projetos.

## 🎯 Índice

- [Calculadora](#calculadora)
- [Tetris Simplificado](#tetris-simplificado)
- [Monitor de Sistema](#monitor-de-sistema)
- [Sequenciador Musical](#sequenciador-musical)
- [Paint Digital](#paint-digital)

---

## 🧮 Calculadora

Calculadora simples com display OLED e navegação por joystick.

```python
from lib.events import *
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer
from lib.config import PINS

def calculadora():
    """Calculadora simples"""
    
    # Hardware
    display = OLEDDisplay()
    buzzer = Buzzer(PINS.BUZZER)
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Estado da calculadora
    display_value = "0"
    operation = None
    stored_value = 0
    cursor_pos = 0
    
    # Layout do teclado
    keypad = [
        ['7', '8', '9', '/'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '-'],
        ['0', '.', '=', '+']
    ]
    
    cursor_x, cursor_y = 0, 0
    
    def render():
        lines = [
            "=== CALCULADORA ===",
            "",
            f"Valor: {display_value}",
            f"Op: {operation or 'None'}",
            "",
            # Mostra teclado
            f"{'>' if cursor_y == 0 else ' '} {' '.join(keypad[0])}",
            f"{'>' if cursor_y == 1 else ' '} {' '.join(keypad[1])}",
            f"{'>' if cursor_y == 2 else ' '} {' '.join(keypad[2])}",
            f"{'>' if cursor_y == 3 else ' '} {' '.join(keypad[3])}"
        ]
        display.draw_lines(lines, valign='top')
    
    def beep():
        buzzer.play_note(800, 0.05)
    
    def process_key(key):
        nonlocal display_value, operation, stored_value
        
        if key.isdigit():
            if display_value == "0":
                display_value = key
            else:
                display_value += key
                
        elif key == '.':
            if '.' not in display_value:
                display_value += '.'
                
        elif key in ['+', '-', '*', '/']:
            stored_value = float(display_value)
            operation = key
            display_value = "0"
            
        elif key == '=':
            if operation and display_value:
                try:
                    current = float(display_value)
                    if operation == '+':
                        result = stored_value + current
                    elif operation == '-':
                        result = stored_value - current
                    elif operation == '*':
                        result = stored_value * current
                    elif operation == '/':
                        result = stored_value / current if current != 0 else 0
                    
                    display_value = str(result)
                    operation = None
                    stored_value = 0
                    
                except:
                    display_value = "ERRO"
    
    # Loop principal
    clock = GameLoop(fps=15)
    clock.start()
    render()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_UP:
                cursor_y = max(0, cursor_y - 1)
                beep()
                render()
                
            elif event == JOYSTICK_DOWN:
                cursor_y = min(3, cursor_y + 1)
                beep()
                render()
                
            elif event == JOYSTICK_LEFT:
                cursor_x = max(0, cursor_x - 1)
                beep()
                render()
                
            elif event == JOYSTICK_RIGHT:
                cursor_x = min(3, cursor_x + 1)
                beep()
                render()
                
            elif event == BUTTON_A_DOWN:
                key = keypad[cursor_y][cursor_x]
                process_key(key)
                buzzer.play_note(1000, 0.1)
                render()
                
            elif event == BUTTON_B_DOWN:
                # Limpar
                display_value = "0"
                operation = None
                stored_value = 0
                buzzer.play_note(400, 0.1)
                render()
        
        clock.tick()

# Executar
calculadora()
```

---

## 🧩 Tetris Simplificado

Versão simples do Tetris para matriz 5x5.

```python
from lib.events import *
from lib.leds import LEDMatrix
from lib.oled import OLEDDisplay
import random

def tetris_mini():
    """Tetris simplificado 5x5"""
    
    # Hardware
    matrix = LEDMatrix()
    display = OLEDDisplay()
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Peças (simplificadas para 5x5)
    pieces = [
        # I-piece (linha)
        [[(0, 0), (1, 0), (2, 0)]],
        # L-piece
        [[(0, 0), (0, 1), (1, 1)]],
        # Square
        [[(0, 0), (1, 0), (0, 1), (1, 1)]],
        # T-piece
        [[(1, 0), (0, 1), (1, 1), (2, 1)]]
    ]
    
    # Estado do jogo
    board = [[False for _ in range(5)] for _ in range(5)]
    current_piece = None
    piece_pos = [2, 0]  # x, y
    piece_type = 0
    score = 0
    fall_timer = 0
    fall_speed = 30  # frames
    
    def spawn_piece():
        nonlocal current_piece, piece_type, piece_pos
        piece_type = random.randint(0, len(pieces) - 1)
        current_piece = pieces[piece_type][0].copy()
        piece_pos = [2, 0]
    
    def can_place_piece(piece, pos):
        for px, py in piece:
            x, y = pos[0] + px, pos[1] + py
            if x < 0 or x >= 5 or y >= 5:
                return False
            if y >= 0 and board[y][x]:
                return False
        return True
    
    def place_piece():
        for px, py in current_piece:
            x, y = piece_pos[0] + px, piece_pos[1] + py
            if 0 <= x < 5 and 0 <= y < 5:
                board[y][x] = True
    
    def clear_lines():
        nonlocal score
        lines_cleared = 0
        for y in range(4, -1, -1):
            if all(board[y]):
                # Remove linha
                del board[y]
                board.insert(0, [False for _ in range(5)])
                lines_cleared += 1
                score += 10
        return lines_cleared
    
    def render():
        matrix.clear()
        
        # Desenha board
        for y in range(5):
            for x in range(5):
                if board[y][x]:
                    matrix.set_pixel(x, y, (255, 255, 255))  # Branco
        
        # Desenha peça atual
        if current_piece:
            for px, py in current_piece:
                x, y = piece_pos[0] + px, piece_pos[1] + py
                if 0 <= x < 5 and 0 <= y < 5:
                    matrix.set_pixel(x, y, (255, 0, 0))  # Vermelho
        
        matrix.show()
        
        # Display
        lines = [
            "=== TETRIS ===",
            f"Score: {score}",
            "",
            "A: Rodar",
            "Joy: Mover",
            "B: Drop"
        ]
        display.draw_lines(lines, valign='middle')
    
    # Inicia jogo
    spawn_piece()
    clock = GameLoop(fps=30)
    clock.start()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_LEFT and current_piece:
                new_pos = [piece_pos[0] - 1, piece_pos[1]]
                if can_place_piece(current_piece, new_pos):
                    piece_pos = new_pos
                    
            elif event == JOYSTICK_RIGHT and current_piece:
                new_pos = [piece_pos[0] + 1, piece_pos[1]]
                if can_place_piece(current_piece, new_pos):
                    piece_pos = new_pos
                    
            elif event == JOYSTICK_DOWN and current_piece:
                new_pos = [piece_pos[0], piece_pos[1] + 1]
                if can_place_piece(current_piece, new_pos):
                    piece_pos = new_pos
                    
            elif event == BUTTON_A_DOWN and current_piece:
                # Rotação simples (não implementada totalmente)
                pass
                
            elif event == BUTTON_B_DOWN and current_piece:
                # Drop rápido
                while can_place_piece(current_piece, [piece_pos[0], piece_pos[1] + 1]):
                    piece_pos[1] += 1
        
        # Queda automática
        fall_timer += 1
        if fall_timer >= fall_speed and current_piece:
            new_pos = [piece_pos[0], piece_pos[1] + 1]
            if can_place_piece(current_piece, new_pos):
                piece_pos = new_pos
            else:
                # Peça pousou
                place_piece()
                clear_lines()
                spawn_piece()
                
                # Verifica game over
                if not can_place_piece(current_piece, piece_pos):
                    print(f"Game Over! Score: {score}")
                    clock.stop()
            
            fall_timer = 0
        
        render()
        clock.tick()

# Executar
tetris_mini()
```

---

## 📊 Monitor de Sistema

Monitor que mostra informações do sistema e sensores.

```python
from lib.events import *
from lib.oled import OLEDDisplay
import gc
import machine

def monitor_sistema():
    """Monitor de sistema e recursos"""
    
    # Hardware
    display = OLEDDisplay()
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Páginas do monitor
    pages = ["Sistema", "Memória", "GPIO", "Rede"]
    current_page = 0
    
    def get_system_info():
        return [
            "=== SISTEMA ===",
            f"Freq: {machine.freq() // 1000000}MHz",
            f"Temp: {machine.temperature():.1f}°C" if hasattr(machine, 'temperature') else "Temp: N/A",
            f"Uptime: {machine.time() // 3600}h",
            "",
            "A: Refresh",
            "Joy: Navegar"
        ]
    
    def get_memory_info():
        free = gc.mem_free()
        alloc = gc.mem_alloc()
        total = free + alloc
        
        return [
            "=== MEMÓRIA ===",
            f"Total: {total // 1024}KB",
            f"Usado: {alloc // 1024}KB",
            f"Livre: {free // 1024}KB",
            f"Uso: {(alloc/total)*100:.1f}%",
            "",
            "A: GC Collect"
        ]
    
    def get_gpio_info():
        return [
            "=== GPIO ===",
            f"OLED: {PINS.OLED_SDA},{PINS.OLED_SCL}",
            f"Joy: {PINS.JOYSTICK_VRX},{PINS.JOYSTICK_VRY}",
            f"Btn: {PINS.BUTTON_A},{PINS.BUTTON_B}",
            f"Buzz: {PINS.BUZZER}",
            f"LEDs: {PINS.NEOPIXEL}",
            "A: Test GPIOs"
        ]
    
    def get_network_info():
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            if wlan.active():
                status = "Conectado" if wlan.isconnected() else "Desconectado"
                ip = wlan.ifconfig()[0] if wlan.isconnected() else "N/A"
            else:
                status = "Inativo"
                ip = "N/A"
        except:
            status = "N/A"
            ip = "N/A"
            
        return [
            "=== REDE ===",
            f"Status: {status}",
            f"IP: {ip}",
            "WiFi: BitDogLab",
            "",
            "A: Toggle WiFi",
            "B: Scan"
        ]
    
    def render():
        if current_page == 0:
            lines = get_system_info()
        elif current_page == 1:
            lines = get_memory_info()
        elif current_page == 2:
            lines = get_gpio_info()
        elif current_page == 3:
            lines = get_network_info()
        
        # Adiciona indicador de página
        lines.append("")
        lines.append(f"Pág {current_page + 1}/{len(pages)}")
        
        display.draw_lines(lines, valign='top')
    
    # Loop principal
    clock = GameLoop(fps=5)  # Atualização lenta
    clock.start()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_LEFT:
                current_page = max(0, current_page - 1)
                
            elif event == JOYSTICK_RIGHT:
                current_page = min(len(pages) - 1, current_page + 1)
                
            elif event == BUTTON_A_DOWN:
                if current_page == 1:  # Memória
                    gc.collect()
                    print("Garbage collection executado")
                elif current_page == 2:  # GPIO
                    print("Teste de GPIO (não implementado)")
                elif current_page == 3:  # Rede
                    print("Toggle WiFi (não implementado)")
                    
            elif event == BUTTON_B_DOWN:
                if current_page == 3:  # Rede
                    print("Scan WiFi (não implementado)")
                else:
                    clock.stop()
        
        render()
        clock.tick()

# Executar
monitor_sistema()
```

---

## 🎵 Sequenciador Musical

Sequenciador simples para criar batidas.

```python
from lib.events import *
from lib.leds import LEDMatrix
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer

def sequenciador():
    """Sequenciador musical 5x5"""
    
    # Hardware
    matrix = LEDMatrix()
    display = OLEDDisplay()
    buzzer = Buzzer(PINS.BUZZER)
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Sequenciador 5x5 (5 instrumentos, 5 steps)
    sequence = [[False for _ in range(5)] for _ in range(5)]
    cursor_x, cursor_y = 0, 0
    current_step = 0
    playing = False
    step_timer = 0
    tempo = 15  # frames por step
    
    # Sons dos instrumentos
    instruments = [
        ("Kick", 60),      # Bumbo - grave
        ("Snare", 200),    # Caixa - médio-grave  
        ("HiHat", 800),    # Chimbal - agudo
        ("Perc1", 400),    # Percussão 1
        ("Perc2", 600)     # Percussão 2
    ]
    
    def render():
        matrix.clear()
        
        # Desenha sequência
        for y in range(5):
            for x in range(5):
                if sequence[y][x]:
                    if x == current_step and playing:
                        matrix.set_pixel(x, y, (255, 255, 0))  # Amarelo (tocando)
                    else:
                        matrix.set_pixel(x, y, (0, 255, 0))    # Verde (ativo)
                elif x == current_step and playing:
                    matrix.set_pixel(x, y, (255, 0, 0))        # Vermelho (step atual)
                else:
                    matrix.set_pixel(x, y, (0, 0, 50))         # Azul escuro (vazio)
        
        # Destaca cursor
        if not playing:
            matrix.set_pixel(cursor_x, cursor_y, (255, 255, 255))  # Branco
        
        matrix.show()
        
        # Display
        lines = [
            "=== SEQUENCIADOR ===",
            f"Instr: {instruments[cursor_y][0]}",
            f"Step: {cursor_x + 1}/5",
            f"Tempo: {60000 // (tempo * 33)}BPM",
            "",
            f"Status: {'▶️ Play' if playing else '⏸️ Stop'}",
            "A: Toggle | B: Play"
        ]
        display.draw_lines(lines, valign='middle')
    
    def play_step():
        for y in range(5):
            if sequence[y][current_step]:
                freq = instruments[y][1]
                buzzer.play_note(freq, 0.1)
    
    # Loop principal
    clock = GameLoop(fps=30)
    clock.start()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_LEFT and not playing:
                cursor_x = max(0, cursor_x - 1)
                
            elif event == JOYSTICK_RIGHT and not playing:
                cursor_x = min(4, cursor_x + 1)
                
            elif event == JOYSTICK_UP and not playing:
                cursor_y = max(0, cursor_y - 1)
                
            elif event == JOYSTICK_DOWN and not playing:
                cursor_y = min(4, cursor_y + 1)
                
            elif event == BUTTON_A_DOWN:
                if not playing:
                    # Toggle step
                    sequence[cursor_y][cursor_x] = not sequence[cursor_y][cursor_x]
                else:
                    # Para
                    playing = False
                    current_step = 0
                    
            elif event == BUTTON_B_DOWN:
                # Play/Stop
                playing = not playing
                if not playing:
                    current_step = 0
        
        # Sequenciador
        if playing:
            step_timer += 1
            if step_timer >= tempo:
                play_step()
                current_step = (current_step + 1) % 5
                step_timer = 0
        
        render()
        clock.tick()

# Executar
sequenciador()
```

---

## 🎨 Paint Digital

Editor de imagens simples para a matriz 5x5.

```python
from lib.events import *
from lib.leds import LEDMatrix
from lib.oled import OLEDDisplay

def paint_digital():
    """Editor de imagens 5x5"""
    
    # Hardware
    matrix = LEDMatrix()
    display = OLEDDisplay()
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Estado do editor
    canvas = [[(0, 0, 0) for _ in range(5)] for _ in range(5)]
    cursor_x, cursor_y = 0, 0
    
    # Paleta de cores
    colors = [
        (255, 0, 0),    # Vermelho
        (0, 255, 0),    # Verde
        (0, 0, 255),    # Azul
        (255, 255, 0),  # Amarelo
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Ciano
        (255, 255, 255),# Branco
        (0, 0, 0)       # Preto (borracha)
    ]
    
    current_color = 0
    mode = "paint"  # "paint" ou "color"
    
    def render():
        matrix.clear()
        
        if mode == "paint":
            # Mostra canvas
            for y in range(5):
                for x in range(5):
                    color = canvas[y][x]
                    if x == cursor_x and y == cursor_y:
                        # Destaca cursor
                        cursor_color = (255, 255, 255) if color == (0, 0, 0) else (0, 0, 0)
                        matrix.set_pixel(x, y, cursor_color)
                    else:
                        matrix.set_pixel(x, y, color)
        
        elif mode == "color":
            # Mostra paleta
            for i, color in enumerate(colors[:5]):
                highlight = (255, 255, 255) if i == current_color else (50, 50, 50)
                matrix.set_pixel(i, 0, color if color != (0, 0, 0) else highlight)
                matrix.set_pixel(i, 1, highlight)
        
        matrix.show()
        
        # Display
        color_name = ["Red", "Green", "Blue", "Yellow", "Magenta", "Cyan", "White", "Black"][current_color]
        
        lines = [
            "=== PAINT ===",
            f"Modo: {mode.title()}",
            f"Cor: {color_name}",
            f"Pos: ({cursor_x},{cursor_y})",
            "",
            "A: Pintar/Sel",
            "B: Modo/Limpar"
        ]
        display.draw_lines(lines, valign='middle')
    
    def save_pattern():
        """Salva padrão atual"""
        print("Padrão atual:")
        for y in range(5):
            line = ""
            for x in range(5):
                r, g, b = canvas[y][x]
                if (r, g, b) == (0, 0, 0):
                    line += "0"
                else:
                    line += "1"
            print(line)
    
    # Loop principal
    clock = GameLoop(fps=20)
    clock.start()
    
    while clock.running:
        poll()
        
        for event in get():
            if mode == "paint":
                if event == JOYSTICK_LEFT:
                    cursor_x = max(0, cursor_x - 1)
                elif event == JOYSTICK_RIGHT:
                    cursor_x = min(4, cursor_x + 1)
                elif event == JOYSTICK_UP:
                    cursor_y = max(0, cursor_y - 1)
                elif event == JOYSTICK_DOWN:
                    cursor_y = min(4, cursor_y + 1)
                elif event == BUTTON_A_DOWN:
                    # Pinta pixel
                    canvas[cursor_y][cursor_x] = colors[current_color]
                elif event == BUTTON_B_DOWN:
                    # Muda para modo cor
                    mode = "color"
                    
            elif mode == "color":
                if event == JOYSTICK_LEFT:
                    current_color = max(0, current_color - 1)
                elif event == JOYSTICK_RIGHT:
                    current_color = min(len(colors) - 1, current_color + 1)
                elif event == BUTTON_A_DOWN:
                    # Seleciona cor
                    mode = "paint"
                elif event == BUTTON_B_DOWN:
                    # Limpa canvas
                    canvas = [[(0, 0, 0) for _ in range(5)] for _ in range(5)]
                    mode = "paint"
            
            # Salvar (qualquer modo)
            if event == JOYSTICK_BUTTON_DOWN:
                save_pattern()
        
        render()
        clock.tick()

# Executar
paint_digital()
```

---

## 🔧 Dicas para Seus Projetos

### 1. **Organização Modular**
```python
# game.py
class Game:
    def __init__(self):
        self.state = "menu"
        self.menu = Menu()
        self.gameplay = Gameplay()
    
    def update(self, events):
        if self.state == "menu":
            self.menu.update(events)
        elif self.state == "play":
            self.gameplay.update(events)
```

### 2. **Estados de Jogo**
```python
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    
    def __init__(self):
        self.current = self.MENU
        self.previous = None
    
    def change(self, new_state):
        self.previous = self.current
        self.current = new_state
```

### 3. **Sistema de Configurações**
```python
# config.py (seu próprio)
class GameConfig:
    VOLUME = 0.5
    FPS = 30
    DIFFICULTY = "normal"
    
    @classmethod
    def save(cls):
        # Salvar em arquivo
        pass
    
    @classmethod
    def load(cls):
        # Carregar de arquivo
        pass
```

### 4. **Efeitos Visuais**
```python
def flash_effect(matrix, color, duration=200):
    """Efeito de flash na matriz"""
    matrix.fill(color)
    matrix.show()
    time.sleep_ms(duration)
    matrix.clear()
    matrix.show()

def fade_effect(led, from_color, to_color, steps=10):
    """Fade entre cores"""
    for i in range(steps):
        factor = i / (steps - 1)
        r = int(from_color[0] + (to_color[0] - from_color[0]) * factor)
        g = int(from_color[1] + (to_color[1] - from_color[1]) * factor)
        b = int(from_color[2] + (to_color[2] - from_color[2]) * factor)
        led.set_color(r, g, b)
        time.sleep_ms(50)
```

Agora você tem uma biblioteca completa de exemplos para se inspirar! Combine e modifique essas ideias para criar seus próprios projetos únicos! 🎮✨
