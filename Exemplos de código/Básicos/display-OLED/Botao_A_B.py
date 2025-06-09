from machine import SoftI2C, Pin
from ssd1306 import SSD1306_I2C
import time

# Configuração do display OLED
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))  # SDA e SCL conectados aos GPIO14 e GPIO15
oled = SSD1306_I2C(128, 64, i2c_oled)         # Resolução do OLED 128x64

# Configuração dos botões
button_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão A no GPIO5
button_b = Pin(6, Pin.IN, Pin.PULL_UP)  # Botão B no GPIO6

def display_messages(lines):
    """Mostra múltiplas linhas no display OLED."""
    oled.fill(0)
    for idx, line in enumerate(lines):
        oled.text(line, 0, 10 + 10 * idx)
    oled.show()

try:
    while True:
        if button_a.value() == 0 and button_b.value() == 0:
            display_messages(["Botao A e B", "pressionados!"])
        elif button_a.value() == 0:
            display_messages(["Botao A", "pressionado!"])
        elif button_b.value() == 0:
            display_messages(["Botao B", "pressionado!"])
        else:
            display_messages(["Aguardando botao..."])

        time.sleep(0.1)

except KeyboardInterrupt:
    oled.fill(0)
    oled.show()

