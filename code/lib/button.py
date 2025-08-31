from machine import Pin
import time

BUTTON_A_PIN = 5
BUTTON_B_PIN = 6

# Estados possíveis do botão
class ButtonState:
    UNCHANGED = "unchanged"
    PRESSED = "pressed"
    RELEASED = "released"
    LONG_PRESS = "long_press"
    WHILE_PRESSED = "while_pressed"

class Button:
    def __init__(self, pin, debounce_ms=50, long_press_ms=1000, repeat_ms=200):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms
        self.long_press_ms = long_press_ms
        self.repeat_ms = repeat_ms

        self.last_state = self.pin.value()
        self.last_time = 0
        self.press_start = 0
        self.last_repeat = 0

        # callbacks
        self.on_press_cb = None
        self.on_release_cb = None
        self.on_long_cb = None
        self.on_while_cb = None

    def is_pressed(self):
        return self.pin.value() == 0

    def read(self):
        """Verifica estado do botão e dispara callbacks"""
        now = time.ticks_ms()
        state = self.pin.value()

        # Mudança de estado (debounced)
        if time.ticks_diff(now, self.last_time) > self.debounce_ms and state != self.last_state:
            self.last_state = state
            self.last_time = now

            if state == 0:  # Pressionado
                self.press_start = now
                self.last_repeat = now
                if self.on_press_cb:
                    self.on_press_cb()
                return ButtonState.PRESSED

            else:  # Liberado
                duration = time.ticks_diff(now, self.press_start)
                if duration >= self.long_press_ms:
                    if self.on_long_cb:
                        self.on_long_cb()
                    return ButtonState.LONG_PRESS
                else:
                    if self.on_release_cb:
                        self.on_release_cb()
                    return ButtonState.RELEASED

        # Enquanto pressionado
        if self.is_pressed() and self.on_while_cb:
            if time.ticks_diff(now, self.last_repeat) >= self.repeat_ms:
                self.on_while_cb()
                self.last_repeat = now
                return ButtonState.WHILE_PRESSED

        return ButtonState.UNCHANGED

    # === Registradores de callbacks ===
    def on_press(self, callback):
        self.on_press_cb = callback

    def on_release(self, callback):
        self.on_release_cb = callback

    def on_long_press(self, callback, duration_ms=None):
        self.on_long_cb = callback
        if duration_ms:
            self.long_press_ms = duration_ms

    def on_while_pressed(self, callback, repeat_ms=None):
        self.on_while_cb = callback
        if repeat_ms:
            self.repeat_ms = repeat_ms


# === Teste prático ===
if __name__ == "__main__":
    button_a = Button(BUTTON_A_PIN)
    button_b = Button(BUTTON_B_PIN)

    # Exemplos de callbacks
    button_a.on_press(lambda: print("[A] Pressionado"))
    button_a.on_release(lambda: print("[A] Liberado"))
    button_a.on_long_press(lambda: print("[A] Long Press"))
    button_a.on_while_pressed(lambda: print("[A] Segurando..."), repeat_ms=500)

    button_b.on_press(lambda: print("[B] Pressionado"))
    button_b.on_release(lambda: print("[B] Liberado"))
    button_b.on_long_press(lambda: print("[B] Long Press"))
    button_b.on_while_pressed(lambda: print("[B] Segurando..."), repeat_ms=300)

    print("=== Teste individual de botões ===")
    print("1. Pressione A ou B")
    print("2. Mantenha para long press / while pressed")
    print("3. Ctrl+C para sair\n")

    try:
        while True:
            button_a.read()
            button_b.read()
            time.sleep_ms(50)
    except KeyboardInterrupt:
        print("\nEncerrado.")
