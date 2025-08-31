# BitDogLab V7 Framework - Documentação

Framework para desenvolvimento de aplicações e jogos no BitDogLab V7 com MicroPython.
Sistema inspirado no Pygame/Godot com controle manual de eventos e loops.

## 📚 Índice

- [Visão Geral](#visão-geral)
- [Sistema de Eventos](#sistema-de-eventos)
- [Hardware](#hardware)
- [Display OLED](#display-oled)
- [Áudio](#áudio)
- [LEDs](#leds)
- [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral

### Filosofia do Framework

O BitDogLab V7 Framework segue a filosofia **"você controla tudo"**:
- **Game Loop Manual**: Você decide quando atualizar
- **Sistema de Eventos**: Como Pygame - polling manual
- **Hardware Abstrato**: Classes simples para cada componente
- **Flexível**: Use apenas o que precisar

### Arquitetura

```
┌─────────────────┐    ┌─────────────────┐
│   SEU CÓDIGO    │    │     EVENTOS     │
│   (Game Loop)   │◄──►│   (Pygame-like) │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│    HARDWARE     │    │   ASSETS        │
│ (OLED,Buzzer,   │    │ (Patterns,      │
│  Joystick,etc)  │    │  Music, SFX)    │
└─────────────────┘    └─────────────────┘
```

---

## 🎮 Sistema de Eventos

### Importação

```python
from lib.events import *
```

### Constantes de Eventos

```python
# Joystick
JOYSTICK_UP = 1      # Movimento para cima
JOYSTICK_DOWN = 2    # Movimento para baixo  
JOYSTICK_LEFT = 3    # Movimento para esquerda
JOYSTICK_RIGHT = 4   # Movimento para direita
JOYSTICK_CENTER = 5  # Volta ao centro
JOYSTICK_BUTTON_DOWN = 6  # Botão do joystick pressionado
JOYSTICK_BUTTON_UP = 7    # Botão do joystick liberado

# Botões
BUTTON_A_DOWN = 10   # Botão A pressionado
BUTTON_A_UP = 11     # Botão A liberado
BUTTON_B_DOWN = 12   # Botão B pressionado
BUTTON_B_UP = 13     # Botão B liberado

# Sistema
QUIT = 99           # Sair da aplicação
```

### Classe Event

```python
class Event:
    """Representa um evento do sistema"""
    
    def __init__(self, event_type, **kwargs):
        self.type = event_type  # Tipo do evento
        self.time = ticks_ms()  # Timestamp
        # kwargs vira atributos do evento
```

**Exemplo:**
```python
# Evento de joystick tem atributos extras
if event.type == JOYSTICK_UP:
    print(f"Direção: {event.direction}")  # "north", "northeast", etc
    print(f"Posição: ({event.x}, {event.y})")  # Valores normalizados
```

### Funções Principais

#### `init_events(joystick, buttons, debug=False)`
Inicializa o sistema de eventos.

```python
from lib.joystick import Joystick
from lib.button import Button
from lib.config import PINS

# Criar hardware
joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}

# Inicializar eventos
init_events(joystick, buttons, debug=True)
```

#### `poll()`
**OBRIGATÓRIO**: Faz polling do hardware para detectar mudanças.

```python
# Chame a cada frame do seu loop
while running:
    poll()  # ← OBRIGATÓRIO!
    # resto do código...
```

#### `get()`
Retorna lista de eventos e limpa a fila.

```python
events = get()
for event in events:
    if event == JOYSTICK_UP:
        print("Joystick para cima!")
```

#### `wait(timeout=None)`
Espera por um evento (bloqueia).

```python
# Espera infinitamente
event = wait()

# Espera com timeout (ms)
event = wait(1000)  # 1 segundo
if event is None:
    print("Timeout!")
```

#### `peek(event_types=None)`
Verifica se há eventos sem removê-los.

```python
# Verifica qualquer evento
if peek():
    print("Há eventos pendentes")

# Verifica eventos específicos
if peek([BUTTON_A_DOWN, BUTTON_B_DOWN]):
    print("Algum botão foi pressionado")
```

#### `clear(event_types=None)`
Limpa eventos da fila.

```python
# Limpa todos
clear()

# Limpa específicos
clear([JOYSTICK_UP, JOYSTICK_DOWN])
```

### Classe GameLoop

Controla FPS e timing do seu loop.

```python
class GameLoop:
    def __init__(self, fps=60)          # Define FPS
    def start(self)                     # Inicia o loop
    def stop(self)                      # Para o loop
    def tick(self)                      # Controla FPS
    def should_update(self)             # Verifica se deve atualizar
```

**Exemplo:**
```python
clock = GameLoop(fps=30)
clock.start()

while clock.running:
    poll()
    
    # Sua lógica aqui
    for event in get():
        handle_event(event)
    
    update_game()
    render()
    
    clock.tick()  # Mantém FPS
```

---

## 🕹️ Hardware

### Configuração de Pinos

```python
from lib.config import PINS

# Pinos disponíveis
PINS.OLED_SDA = 14          # GPIO14 - OLED SDA
PINS.OLED_SCL = 15          # GPIO15 - OLED SCL
PINS.BUTTON_A = 5           # GPIO5  - Botão A
PINS.BUTTON_B = 6           # GPIO6  - Botão B
PINS.JOYSTICK_VRX = 27      # GPIO27 - Joystick X
PINS.JOYSTICK_VRY = 26      # GPIO26 - Joystick Y
PINS.JOYSTICK_BUTTON = 22   # GPIO22 - Botão Joystick
PINS.BUZZER = 21            # GPIO21 - Buzzer
PINS.LED_RED = 13           # GPIO13 - LED RGB Vermelho
PINS.LED_GREEN = 11         # GPIO11 - LED RGB Verde
PINS.LED_BLUE = 12          # GPIO12 - LED RGB Azul
PINS.NEOPIXEL = 7           # GPIO7  - Matriz NeoPixel
```

### Joystick

```python
from lib.joystick import Joystick

class Joystick:
    def __init__(self, pin_x, pin_y, pin_btn=None, 
                 deadzone_x=5000, deadzone_y=5000,
                 invert_x=False, invert_y=False)
```

**Métodos Principais:**
```python
joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON,
                   deadzone_x=3000, deadzone_y=3000, invert_y=True)

# Leitura básica
raw_x, raw_y = joystick.read_raw()        # Valores 0-65535
norm_x, norm_y = joystick.get_normalized() # Valores -1.0 a 1.0

# Direção
direction = joystick.get_direction()       # "north", "center", etc
angle = joystick.get_angle()              # 0-360 graus ou None

# Botão
pressed = joystick.is_pressed()           # True/False
joystick.wait_for_release()               # Aguarda soltar

# Configuração
joystick.set_debug(True)                  # Ativa debug
joystick.calibrate(samples=100)           # Recalibra centro
```

**Direções Retornadas:**
- `"center"` - Joystick centralizado
- `"north"`, `"south"`, `"east"`, `"west"` - Direções cardeais
- `"northeast"`, `"northwest"`, `"southeast"`, `"southwest"` - Diagonais

### Botões

```python
from lib.button import Button

class Button:
    def __init__(self, pin, pull_up=True, debounce_time=50)
```

**Métodos:**
```python
button_a = Button(PINS.BUTTON_A)

# Estado
pressed = button_a.is_pressed()           # True/False
released = button_a.is_released()         # True/False

# Espera
button_a.wait_for_press()                 # Aguarda pressionar
button_a.wait_for_release()               # Aguarda soltar

# Callbacks
def on_press():
    print("Pressionado!")

button_a.set_callback(on_press)
button_a.check()  # Chama callback se necessário
```

---

## 🖥️ Display OLED

### Classe OLEDDisplay

```python
from lib.oled import OLEDDisplay

class OLEDDisplay:
    def __init__(self, width=128, height=64, sda=14, scl=15, address=0x3C)
```

**Métodos Básicos:**
```python
display = OLEDDisplay()

# Controle básico
display.clear()                           # Limpa tela
display.show()                            # Atualiza display
display.fill(color)                       # Preenche (0=preto, 1=branco)

# Texto
display.text("Hello", x=10, y=20)         # Texto em posição
display.draw_text("Hello", x=0, y=0, align='center')  # Com alinhamento

# Desenho
display.pixel(x, y, color)                # Pixel individual
display.line(x1, y1, x2, y2, color)       # Linha
display.rect(x, y, w, h, color, fill=False) # Retângulo
```

**Método Avançado - draw_lines():**
```python
# Texto simples
lines = ["Linha 1", "Linha 2", "Linha 3"]
display.draw_lines(lines, valign='middle')

# Texto com alinhamento individual
lines = [
    "Título",
    {"text": "Centro", "align": "center"},
    {"text": "Direita", "align": "right"}
]
display.draw_lines(lines, valign='top', global_align='left')
```

**Parâmetros do draw_lines():**
- `valign`: `'top'`, `'middle'`, `'bottom'` - Alinhamento vertical
- `global_align`: `'left'`, `'center'`, `'right'` - Alinhamento padrão
- Cada linha pode ser:
  - String simples: `"Texto"`
  - Dict: `{"text": "Texto", "align": "center"}`

**Exemplo Completo:**
```python
display = OLEDDisplay()

if display.is_present:
    display.clear()
    
    # Menu simples
    lines = [
        "=== MENU ===",
        "",
        "> Opção 1",
        "  Opção 2", 
        "  Opção 3"
    ]
    
    display.draw_lines(lines, valign='middle')
    print("Menu exibido!")
else:
    print("Display não conectado")
```

---

## 🔊 Áudio

### Buzzer

```python
from lib.buzzer import Buzzer

class Buzzer:
    def __init__(self, pin, default_volume=0.3, pwm_frequency=1000)
```

**Métodos:**
```python
buzzer = Buzzer(PINS.BUZZER)

# Sons básicos
buzzer.play_note(frequency=440, duration=0.5, volume=0.3)  # Lá por 0.5s
buzzer.stop()                                              # Para som

# Efeitos
buzzer.fade_in(freq=1000, volume=0.5, duration=1.0)       # Fade in
buzzer.fade_out(duration=1.0)                             # Fade out
buzzer.play_note_with_fade(freq=880, duration=2.0,        # Com fade
                          fade_in_time=0.3, fade_out_time=0.3)

# Volume
buzzer.set_volume(0.5)                                     # 0.0 a 1.0
```

**Constantes de Notas:**
```python
from lib.buzzer import NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4

# Escala Dó maior
notes = [NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4]
for note in notes:
    buzzer.play_note(note, 0.3)
    time.sleep(0.1)
```

**Tocar Arquivos de Música:**
```python
# Arquivos em assets/audio/music/
buzzer.play_audio_file("assets/audio/music/mario.txt")

# Função global
from lib.buzzer import play_audio
play_audio(PINS.BUZZER, "assets/audio/ui/click.txt", volume=0.3)
```

---

## 💡 LEDs

### LED RGB Central

```python
from lib.leds import CentralLED

led = CentralLED()

# Cores básicas
led.red()                                 # Vermelho
led.green()                               # Verde  
led.blue()                                # Azul
led.white()                               # Branco
led.off()                                 # Desliga

# Cores customizadas
led.set_color(255, 128, 0)                # Laranja (R, G, B)
led.set_rgb(red=255, green=0, blue=255)   # Magenta

# Efeitos
led.fade_to_color(255, 0, 0, duration=1000)  # Fade para vermelho
led.breathe(color=(0, 255, 0), cycles=3)     # Efeito respiração
led.rainbow_cycle(duration=2000)             # Ciclo arco-íris
```

### Matriz NeoPixel 5x5

```python
from lib.leds import LEDMatrix

matrix = LEDMatrix()

# Controle individual
matrix.set_pixel(x=2, y=2, color=(255, 0, 0))  # Pixel central vermelho
matrix.show()                                   # Atualiza display

# Padrões
matrix.clear()                                  # Limpa tudo
matrix.fill((0, 255, 0))                       # Tudo verde
matrix.test_pattern()                           # Padrão de teste

# Carregar padrões de arquivo
matrix.load_pattern("assets/patterns/heart.txt")
matrix.load_pattern("assets/patterns/smile.txt")

# Efeitos
matrix.wave_effect(color=(0, 0, 255), speed=100)    # Onda azul
matrix.spiral_effect(color=(255, 255, 0), speed=50) # Espiral amarela
```

**Coordenadas da Matriz:**
```
(0,0) (1,0) (2,0) (3,0) (4,0)
(0,1) (1,1) (2,1) (3,1) (4,1)
(0,2) (1,2) (2,2) (3,2) (4,2)
(0,3) (1,3) (2,3) (3,3) (4,3)
(0,4) (1,4) (2,4) (3,4) (4,4)
```

---

## 📁 Sistema de Assets

### Estrutura de Pastas

```
assets/
├── audio/
│   ├── music/          # Músicas (.txt)
│   ├── sfx/            # Efeitos sonoros (.txt)
│   ├── ui/             # Sons de interface (.txt)
│   └── game/           # Sons de jogos (.txt)
└── patterns/           # Padrões para LEDs (.txt)
```

### Formatos de Arquivo

#### Música (assets/audio/)
```
# Arquivo: mario.txt
# Tempo: 120 BPM
NOTE_C4:4 NOTE_D4:4 NOTE_E4:2 REST:4
NOTE_F4:8 NOTE_G4:8 NOTE_A4:1
```

#### Padrões LED (assets/patterns/)
```
# Arquivo: heart.txt
# 5x5 matrix pattern
00000
01010
11111
01110
00100
```

---

## 🚀 Exemplos Práticos

### Exemplo 1: Menu Simples

```python
from lib.events import *
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer
from lib.joystick import Joystick
from lib.button import Button
from lib.config import PINS

def menu_simples():
    # Hardware
    display = OLEDDisplay()
    buzzer = Buzzer(PINS.BUZZER)
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    # Eventos
    init_events(joystick, buttons)
    
    # Estado do menu
    options = ["Jogar", "Configurações", "Sair"]
    selected = 0
    
    def render_menu():
        lines = ["=== MENU ===", ""]
        for i, option in enumerate(options):
            prefix = "> " if i == selected else "  "
            lines.append(f"{prefix}{option}")
        display.draw_lines(lines, valign='middle')
    
    # Loop principal
    clock = GameLoop(fps=15)
    clock.start()
    render_menu()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_UP:
                selected = max(0, selected - 1)
                buzzer.play_note(600, 0.1)
                render_menu()
                
            elif event == JOYSTICK_DOWN:
                selected = min(len(options) - 1, selected + 1)
                buzzer.play_note(600, 0.1)
                render_menu()
                
            elif event == BUTTON_A_DOWN:
                buzzer.play_note(1000, 0.15)
                print(f"Selecionado: {options[selected]}")
                if options[selected] == "Sair":
                    clock.stop()
        
        clock.tick()

# Executar
menu_simples()
```

### Exemplo 2: Jogo Simples - Snake

```python
from lib.events import *
from lib.oled import OLEDDisplay
from lib.leds import LEDMatrix
import random

def snake_game():
    # Hardware
    display = OLEDDisplay()
    matrix = LEDMatrix()
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Estado do jogo
    snake = [(2, 2)]  # Posição inicial
    direction = (1, 0)  # Direita
    food = (4, 4)
    score = 0
    
    def render_game():
        matrix.clear()
        
        # Desenha cobra
        for segment in snake:
            matrix.set_pixel(segment[0], segment[1], (0, 255, 0))  # Verde
        
        # Desenha comida
        matrix.set_pixel(food[0], food[1], (255, 0, 0))  # Vermelho
        
        matrix.show()
        
        # Display
        lines = [
            "=== SNAKE ===",
            f"Score: {score}",
            "",
            "Use Joystick",
            "A: Pause"
        ]
        display.draw_lines(lines, valign='middle')
    
    def move_snake():
        nonlocal food, score
        
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # Verifica bordas
        if (new_head[0] < 0 or new_head[0] >= 5 or 
            new_head[1] < 0 or new_head[1] >= 5):
            return False  # Game over
        
        # Verifica colisão consigo mesmo
        if new_head in snake:
            return False
        
        snake.insert(0, new_head)
        
        # Verifica se comeu
        if new_head == food:
            score += 1
            # Gera nova comida
            while True:
                food = (random.randint(0, 4), random.randint(0, 4))
                if food not in snake:
                    break
        else:
            snake.pop()  # Remove cauda
        
        return True
    
    # Game loop
    clock = GameLoop(fps=3)  # Snake lento
    clock.start()
    paused = False
    render_game()
    
    while clock.running:
        poll()
        
        for event in get():
            # Controles
            if event == JOYSTICK_UP and direction != (0, 1):
                direction = (0, -1)
            elif event == JOYSTICK_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event == JOYSTICK_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event == JOYSTICK_RIGHT and direction != (-1, 0):
                direction = (1, 0)
            elif event == BUTTON_A_DOWN:
                paused = not paused
        
        # Update
        if not paused:
            if not move_snake():
                print(f"Game Over! Score: {score}")
                clock.stop()
            render_game()
        
        clock.tick()

# Executar
snake_game()
```

### Exemplo 3: Player de Música

```python
from lib.events import *
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer
import os

def music_player():
    # Hardware
    display = OLEDDisplay()
    buzzer = Buzzer(PINS.BUZZER)
    joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
    buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
    
    init_events(joystick, buttons)
    
    # Lista de músicas
    music_path = "assets/audio/music"
    songs = [f for f in os.listdir(music_path) if f.endswith('.txt')]
    current_song = 0
    playing = False
    
    def render_player():
        lines = [
            "=== MUSIC PLAYER ===",
            "",
            f"♪ {songs[current_song]}" if songs else "Nenhuma música",
            "",
            "A: Play/Stop",
            "Joy: Navegar",
            f"Status: {'▶️ Playing' if playing else '⏸️ Stopped'}"
        ]
        display.draw_lines(lines, valign='middle')
    
    # Loop principal
    clock = GameLoop(fps=10)
    clock.start()
    render_player()
    
    while clock.running:
        poll()
        
        for event in get():
            if event == JOYSTICK_UP and songs:
                current_song = max(0, current_song - 1)
                render_player()
                
            elif event == JOYSTICK_DOWN and songs:
                current_song = min(len(songs) - 1, current_song + 1)
                render_player()
                
            elif event == BUTTON_A_DOWN and songs:
                if not playing:
                    # Tocar música (não-bloqueante seria ideal)
                    song_file = f"{music_path}/{songs[current_song]}"
                    print(f"Tocando: {songs[current_song]}")
                    # buzzer.play_audio_file(song_file)  # Bloqueante
                playing = not playing
                render_player()
                
            elif event == BUTTON_B_DOWN:
                clock.stop()
        
        clock.tick()

# Executar
music_player()
```

---

## 🔧 Dicas e Boas Práticas

### 1. **Sempre Chame poll()**
```python
# ❌ ERRADO
while running:
    for event in get():  # Nunca terá eventos!
        handle_event(event)

# ✅ CORRETO  
while running:
    poll()  # Obrigatório!
    for event in get():
        handle_event(event)
```

### 2. **Controle de FPS**
```python
# Use GameLoop para FPS consistente
clock = GameLoop(fps=30)  # 30 FPS para jogos
clock = GameLoop(fps=10)  # 10 FPS para menus

while clock.running:
    # sua lógica
    clock.tick()  # Mantém FPS
```

### 3. **Debug de Eventos**
```python
# Ative debug para diagnóstico
init_events(joystick, buttons, debug=True)

# Mostra todos os eventos
for event in get():
    print(f"Evento: {event}")
```

### 4. **Gerenciamento de Estado**
```python
# Use classes para organizar estado
class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.paused = False
    
    def handle_event(self, event):
        if event == BUTTON_A_DOWN:
            self.paused = not self.paused
```

### 5. **Renderização Eficiente**
```python
# Só renderize quando necessário
needs_redraw = True

while running:
    poll()
    
    for event in get():
        handle_event(event)
        needs_redraw = True
    
    if needs_redraw:
        render()
        needs_redraw = False
    
    clock.tick()
```

---

## 📋 Referência Rápida

### Eventos Mais Usados
```python
JOYSTICK_UP, JOYSTICK_DOWN, JOYSTICK_LEFT, JOYSTICK_RIGHT
BUTTON_A_DOWN, BUTTON_B_DOWN
JOYSTICK_BUTTON_DOWN
```

### Template Básico
```python
from lib.events import *
from lib.config import PINS

# Hardware setup
joystick = Joystick(PINS.JOYSTICK_VRX, PINS.JOYSTICK_VRY, PINS.JOYSTICK_BUTTON)
buttons = {'a': Button(PINS.BUTTON_A), 'b': Button(PINS.BUTTON_B)}
init_events(joystick, buttons)

# Game loop
clock = GameLoop(fps=30)
clock.start()

while clock.running:
    poll()
    
    for event in get():
        # Sua lógica aqui
        pass
    
    # Update e render
    clock.tick()
```

### Estrutura de Projeto Recomendada
```
meu_projeto/
├── main.py              # Ponto de entrada
├── game.py              # Lógica principal
├── states.py            # Estados do jogo
└── assets/              # Recursos
    ├── audio/
    └── patterns/
```

---

Agora você tem controle total sobre seu programa! Use este framework para criar jogos, interfaces, players de música, ou qualquer aplicação que imaginar! 🎮✨
