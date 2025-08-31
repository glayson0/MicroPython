from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

# Configurações do display OLED
I2C_SCL_PIN = 15
I2C_SDA_PIN = 14

class OledScreen:
    def __init__(self, width=128, height=64, line_height=8):
        i2c_oled = SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
        oled_hw = SSD1306_I2C(128, 64, i2c_oled)

        self.oled = oled_hw
        self.width = width
        self.height = height
        self.line_height = line_height

    def clear(self):
        self.oled.fill(0)
        self.oled.show()

    def draw_text(self, text, x=0, y=0, align='left'):
        if align == 'center':
            x = max((self.width - len(text)*8)//2, 0)
        elif align == 'right':
            x = max(self.width - len(text)*8, 0)
        self.oled.text(text, x, y)

    def draw_lines(self, lines, valign='top', global_align='left'):
        """
        lines: lista de dicts {'text': str, 'align': optional str}
        valign: 'top', 'middle', 'bottom'
        global_align: alinhamento padrão
        """
        self.clear()
        total_height = len(lines) * self.line_height
        if valign == 'top':
            y_offset = 0
        elif valign == 'middle':
            y_offset = max((self.height - total_height)//2, 0)
        elif valign == 'bottom':
            y_offset = max(self.height - total_height, 0)
        else:
            y_offset = 0

        for i, line in enumerate(lines):
            text = line.get('text', '')
            align = line.get('align', global_align)
            y = y_offset + i*self.line_height
            self.draw_text(text, 0, y, align)

        self.oled.show()