from machine import ADC, Pin
import time

# Pinos padrão do joystick
JOYSTICK_X_PIN = 27
JOYSTICK_Y_PIN = 26
JOYSTICK_BTN_PIN = 22

# Direções como strings
DIRECTIONS = (
    "center", "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest"
)

class Joystick:
    def __init__(self, pin_x, pin_y, pin_btn=None, deadzone_x=5000, deadzone_y=5000):
        self.x = ADC(pin_x)
        self.y = ADC(pin_y)
        self.btn = Pin(pin_btn, Pin.IN, Pin.PULL_UP) if pin_btn is not None else None

        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y

        self.center_x = self.x.read_u16()
        self.center_y = self.y.read_u16()

        self._btn_callback = None
        self._last_btn_state = self.is_pressed()

    # === Leitura dos valores ===
    def read_raw(self):
        return self.x.read_u16(), self.y.read_u16()

    def get_normalized(self):
        raw_x, raw_y = self.read_raw()
        max_x = max(self.center_x, 65535 - self.center_x)
        max_y = max(self.center_y, 65535 - self.center_y)
        norm_x = (raw_x - self.center_x) / max_x if max_x != 0 else 0
        norm_y = (raw_y - self.center_y) / max_y if max_y != 0 else 0
        if abs(norm_x) < self.deadzone_x / max_x:
            norm_x = 0
        if abs(norm_y) < self.deadzone_y / max_y:
            norm_y = 0
        return norm_x, norm_y

    def get_direction(self):
        raw_x, raw_y = self.read_raw()
        dx = raw_x - self.center_x
        dy = raw_y - self.center_y

        if abs(dx) < self.deadzone_x and abs(dy) < self.deadzone_y:
            return "center"

        import math
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360

        if 22.5 <= angle < 67.5:
            return "northeast"
        elif 67.5 <= angle < 112.5:
            return "north"
        elif 112.5 <= angle < 157.5:
            return "northwest"
        elif 157.5 <= angle < 202.5:
            return "west"
        elif 202.5 <= angle < 247.5:
            return "southwest"
        elif 247.5 <= angle < 292.5:
            return "south"
        elif 292.5 <= angle < 337.5:
            return "southeast"
        else:
            return "east"

    def is_pressed(self):
        if self.btn is not None:
            return self.btn.value() == 0
        return False

    # === Calibração ===
    def calibrate(self, samples=100):
        sum_x = sum(self.x.read_u16() for _ in range(samples))
        sum_y = sum(self.y.read_u16() for _ in range(samples))
        self.center_x = sum_x // samples
        self.center_y = sum_y // samples

    # === Callback do botão ===
    def on_press(self, callback):
        self._btn_callback = callback

    def check_button(self):
        if self._btn_callback is not None:
            current = self.is_pressed()
            if current and not self._last_btn_state:
                self._btn_callback()
            self._last_btn_state = current

    # === Leitura completa ===
    def read(self):
        norm_x, norm_y = self.get_normalized()
        return {
            "raw": self.read_raw(),
            "norm": (norm_x, norm_y),
            "dir": self.get_direction(),
            "pressed": self.is_pressed()
        }

# Instância padrão
joystick = Joystick(JOYSTICK_X_PIN, JOYSTICK_Y_PIN, JOYSTICK_BTN_PIN)

# === Teste rápido ===
if __name__ == "__main__":
    j = Joystick(JOYSTICK_X_PIN, JOYSTICK_Y_PIN, JOYSTICK_BTN_PIN)
    print("Teste do Joystick. Pressione Ctrl+C para sair.")

    def pressed_callback():
        print("Botão pressionado!")

    j.on_press(pressed_callback)

    while True:
        data = j.read()
        print(f"X: {data['norm'][0]:.2f}, Y: {data['norm'][1]:.2f}, Direção: {data['dir']}, Pressionado: {data['pressed']}")
        j.check_button()
        time.sleep(0.2)
