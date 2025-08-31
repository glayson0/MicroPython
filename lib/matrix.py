# Importação das Bibliotecas: Importa as bibliotecas Pin e neopixel necessárias para controlar os LEDs
import neopixel
from machine import Pin
from time import sleep

# Configuração inicial
NUM_LEDS = 25  # define que é uma matriz com 25 LEDs
ledsPIN = 7

# Cores
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
colors = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE]
GLOBAL_BRIGHTNESS = 0.1

class LEDMatrix:
    def __init__(self, pin: int, size: int):
        self.np = neopixel.NeoPixel(Pin(pin), size)
        self.size = size
        self.width = int(size**0.5)
        
        # Dicionários contendo os padrões para setas e formas
        self.patterns = {
            "north": [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (4, 2), (0, 2), (3, 3), (1, 3)],
            "south": [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (4, 2), (0, 2), (3, 1), (1, 1)],
            "west": [(2, 0), (3, 1), (2, 2), (3, 3), (2, 4), (4, 2), (0, 2), (3, 2), (1, 2)],
            "east": [(2, 0), (1, 1), (2, 2), (1, 3), (2, 4), (4, 2), (0, 2), (3, 2), (1, 2)],
            "northwest": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (1, 4), (2, 4), (3, 4), (4, 1), (4, 2), (4, 3)],
            "northeast": [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4)],
            "southwest": [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 0), (2, 0), (3, 0), (4, 1), (4, 2), (4, 3)],
            "southeast": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (1, 0), (2, 0), (3, 0), (0, 2), (0, 1), (0, 3)],
            "cross": [(0, 0), (4, 0), (1, 1), (3, 1), (2, 2), (1, 3), (3, 3), (0, 4), (4, 4)],
            "circle": [(1, 0), (2, 0), (3, 0), (0, 1), (4, 1), (0, 2), (4, 2), (0, 3), (4, 3), (1, 4), (2, 4), (3, 4)],
            "plus": [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (4, 2), (2, 3), (0, 2), (3, 2), (1, 2)],
            "minus": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
            "square": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (2, 4), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1)],
            "heart": [(2, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (1, 4), (3, 4)],
            "giraffe": [(1, 0), (3, 0), (1, 1), (2, 1), (3, 1), (1, 2), (1, 3), (0, 4), (1, 4)],
            "small_square": [(1, 1), (2, 1), (3, 1), (1, 2), (3, 2), (1, 3), (2, 3), (3, 3)],
            "smile": [(0, 1), (1, 0), (2, 0), (3, 0), (4, 1), (1, 2), (1, 3), (1, 4), (3, 2), (3, 3), (3, 4)]
        }

    def set_pattern(self, pattern: list, color: tuple[int, int, int], brightness: float=1):
        for coord in pattern:
            self.set_led(coord, color, brightness)

    def set_led(self, coord: tuple[int, int], color: tuple[int, int, int], brightness: float = 1):
        x, y = coord

        # Linearização em serpentina
        if y % 2 == 0:  # linha par (esquerda -> direita)
            index = y * self.width + x
        else:           # linha ímpar (direita -> esquerda)
            index = y * self.width + (self.width - 1 - x)

        self.np[index] = tuple(int(c * brightness) for c in color)

        
    def draw(self):
        self.np.write()
    
    def clear(self):
        self.np.fill((0, 0, 0))
        self.np.write()
    
    def show(self):
        for i in range(self.size):
            print(self.np[i])

if __name__ == "__main__":
    m = LEDMatrix(ledsPIN, NUM_LEDS)

    for y in range(5):
        for x in range(5):
            m.clear()
            m.set_led((x, y), WHITE, GLOBAL_BRIGHTNESS)
            m.draw()
            sleep(0.2)

    for pattern in m.patterns:
        m.clear()
        m.set_pattern(m.patterns[pattern], WHITE, GLOBAL_BRIGHTNESS)
        m.draw()
        sleep(1)