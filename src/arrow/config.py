# Configurações globais do projeto
from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
import neopixel


# Matriz de LEDs (Neopixel)
NUM_LEDS = 25  # Total de LEDs na matriz 5x5
PIN = 7        # Pino onde a matriz Neopixel está conectada

# Display OLED
I2C_SCL_PIN = 15
I2C_SDA_PIN = 14
i2c_oled = SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
oled = SSD1306_I2C(128, 64, i2c_oled)

# Joystick (eixos analógicos)
JOYSTICK_X_PIN = 27
JOYSTICK_Y_PIN = 26
joystick_x = ADC(JOYSTICK_X_PIN)
joystick_y = ADC(JOYSTICK_Y_PIN)

# Classes utilitárias
class Screen:
    def __init__(self, oled, max_lines=8):
        self.oled = oled
        self.lines = []
        self.max_lines = max_lines

    def append(self, text):
        if len(self.lines) >= self.max_lines:
            self.lines.pop(0)
        self.lines.append(text)

    def update_line(self, index, text):
        if 0 <= index < len(self.lines):
            self.lines[index] = text

    def draw(self):
        self.oled.fill(0)
        for i, line in enumerate(self.lines):
            self.oled.text(line, 0, i * 8)
        self.oled.show()

    def clear(self):
        self.lines = []
        self.oled.fill(0)
        self.oled.show()

class Joystick:
    def __init__(self, pin_x, pin_y):
        self.x = ADC(pin_x)
        self.y = ADC(pin_y)

matrix = Matrix(PIN, NUM_LEDS)
joystick = Joystick(JOYSTICK_X_PIN, JOYSTICK_Y_PIN)