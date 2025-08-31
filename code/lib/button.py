"""
Classe Button Genérica para MicroPython
Suporta qualquer botão digital com pull-up interno
Compatível com botões normalmente abertos (active-low)
"""

from machine import Pin
import time

# Estados possíveis do botão
class ButtonState:
    UNCHANGED = "unchanged"
    PRESSED = "pressed"
    RELEASED = "released"
    LONG_PRESS = "long_press"
    WHILE_PRESSED = "while_pressed"

class Button:
    """
    Classe genérica para controle de botão digital
    
    Parâmetros:
    - pin: GPIO do botão (obrigatório)
    - pull_up: Usa pull-up interno (padrão: True)
    - active_low: Botão ativo em LOW (padrão: True)
    - debounce_ms: Tempo de debounce em ms (padrão: 100)
    - long_press_ms: Tempo para long press em ms (padrão: 1000)
    - repeat_ms: Intervalo de repetição em ms (padrão: 200)
    """
    
    def __init__(self, pin, pull_up=True, active_low=True, debounce_ms=100, 
                 long_press_ms=1000, repeat_ms=200):
        """
        Inicializa botão genérico
        
        Args:
            pin: Número do pino GPIO (obrigatório)
            pull_up: Usa pull-up interno
            active_low: Botão ativo em LOW (normalmente aberto)
            debounce_ms: Tempo de debounce
            long_press_ms: Tempo para long press
            repeat_ms: Intervalo de repetição while pressed
        """
        self.pin_number = pin
        self.active_low = active_low
        
        # Configura pino com pull-up se solicitado
        if pull_up:
            self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        else:
            self.pin = Pin(pin, Pin.IN)
        
        # Configurações de timing
        self.debounce_ms = debounce_ms
        self.long_press_ms = long_press_ms
        self.repeat_ms = repeat_ms

        # Estado interno
        self.last_state = self._read_pin()
        self.last_time = 0
        self.press_start = 0
        self.last_repeat = 0

        # Callbacks
        self.on_press_cb = None
        self.on_release_cb = None
        self.on_long_cb = None
        self.on_while_cb = None
        
        # Flag para debug
        self._debug = False
    
    def _read_pin(self):
        """Lê o pino considerando active_low"""
        value = self.pin.value()
        return not value if self.active_low else value

    def set_debug(self, enabled):
        """Ativa/desativa modo debug"""
        self._debug = enabled
        if enabled:
            print(f"Button Debug: GPIO{self.pin_number}, Active={'LOW' if self.active_low else 'HIGH'}")

    def is_pressed(self):
        """Verifica se botão está pressionado"""
        return self._read_pin()

    def read(self):
        """Verifica estado do botão e dispara callbacks"""
        now = time.ticks_ms()
        state = self._read_pin()

        # Mudança de estado (debounced)
        if time.ticks_diff(now, self.last_time) > self.debounce_ms and state != self.last_state:
            self.last_state = state
            self.last_time = now

            if state:  # Pressionado (considerando active_low)
                self.press_start = now
                self.last_repeat = now
                if self.on_press_cb:
                    self.on_press_cb()
                if self._debug:
                    print(f"Botao GPIO{self.pin_number} pressionado")
                return ButtonState.PRESSED

            else:  # Liberado
                duration = time.ticks_diff(now, self.press_start)
                if duration >= self.long_press_ms:
                    if self.on_long_cb:
                        self.on_long_cb()
                    if self._debug:
                        print(f"Botao GPIO{self.pin_number} long press ({duration}ms)")
                    return ButtonState.LONG_PRESS
                else:
                    if self.on_release_cb:
                        self.on_release_cb()
                    if self._debug:
                        print(f"Botao GPIO{self.pin_number} liberado")
                    return ButtonState.RELEASED

        # Enquanto pressionado
        if self.is_pressed() and self.on_while_cb:
            if time.ticks_diff(now, self.last_repeat) >= self.repeat_ms:
                self.on_while_cb()
                self.last_repeat = now
                if self._debug:
                    print(f"Botao GPIO{self.pin_number} while pressed")
                return ButtonState.WHILE_PRESSED

        return ButtonState.UNCHANGED

    # === Registradores de callbacks ===
    def on_press(self, callback):
        """Define callback para pressionamento"""
        self.on_press_cb = callback
        if self._debug:
            print(f"Callback press configurado para GPIO{self.pin_number}")

    def on_release(self, callback):
        """Define callback para liberação"""
        self.on_release_cb = callback
        if self._debug:
            print(f"Callback release configurado para GPIO{self.pin_number}")

    def on_long_press(self, callback, duration_ms=None):
        """Define callback para long press"""
        self.on_long_cb = callback
        if duration_ms:
            self.long_press_ms = duration_ms
        if self._debug:
            print(f"Callback long press configurado para GPIO{self.pin_number} ({self.long_press_ms}ms)")

    def on_while_pressed(self, callback, repeat_ms=None):
        """Define callback para while pressed"""
        self.on_while_cb = callback
        if repeat_ms:
            self.repeat_ms = repeat_ms
        if self._debug:
            print(f"Callback while pressed configurado para GPIO{self.pin_number} ({self.repeat_ms}ms)")
    
    # === Métodos Utilitários ===
    
    def get_info(self):
        """Retorna informações de configuração do botão"""
        return {
            "pin": self.pin_number,
            "active_low": self.active_low,
            "debounce_ms": self.debounce_ms,
            "long_press_ms": self.long_press_ms,
            "repeat_ms": self.repeat_ms,
            "debug": self._debug
        }
    
    def __str__(self):
        """Representação em string do botão"""
        return f"Button(GPIO{self.pin_number}, Active={'LOW' if self.active_low else 'HIGH'})"


# === Factory Function para BitDogLab ===
def create_bitdoglab_button(button_name):
    """Factory function para criar botões configurados para BitDogLab V7"""
    try:
        from config import PINS
        
        button_pins = {
            'A': PINS.BUTTON_A,      # GPIO5 
            'B': PINS.BUTTON_B,      # GPIO6
            'JOYSTICK': PINS.JOYSTICK_BUTTON  # GPIO22
        }
        
        if button_name.upper() not in button_pins:
            raise ValueError(f"Botão '{button_name}' não existe. Disponíveis: {list(button_pins.keys())}")
        
        return Button(
            pin=button_pins[button_name.upper()],
            pull_up=True,      # BitDogLab usa pull-up interno
            active_low=True,   # Botões ativam em LOW (GND)
            debounce_ms=100,   # 100ms de debounce
            long_press_ms=1000,
            repeat_ms=200
        )
    except ImportError:
        raise ImportError("Módulo 'config' não encontrado. Use Button() diretamente.")


def test_button_hardware():
    """Testa o hardware dos botões para detectar problemas"""
    try:
        from config import PINS
        
        print("=== TESTE DE HARDWARE DOS BOTOES ===")
        
        button_pins = {
            'A': PINS.BUTTON_A,      # GPIO5
            'B': PINS.BUTTON_B,      # GPIO6  
            'JOYSTICK': PINS.JOYSTICK_BUTTON  # GPIO22
        }
        
        working_buttons = []
        problem_buttons = []
        
        for name, pin_num in button_pins.items():
            print(f"Testando botao {name} (GPIO{pin_num})...")
            
            # Cria botão temporário
            test_pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
            
            # Lê valor inicial
            initial_value = test_pin.value()
            
            # Espera um pouco e lê novamente
            time.sleep_ms(100)
            second_value = test_pin.value()
            
            if initial_value == 1 and second_value == 1:
                print(f"  OK Botao {name}: OK (HIGH, nao pressionado)")
                working_buttons.append(name)
            elif initial_value == 0 and second_value == 0:
                print(f"  PROBLEMA Botao {name}: SEMPRE LOW (problema de hardware ou botao travado)")
                problem_buttons.append(name)
            else:
                print(f"  INSTAVEL Botao {name}: INSTAVEL (valores {initial_value}/{second_value})")
                problem_buttons.append(name)
        
        print(f"\nRESULTADO:")
        print(f"Botoes funcionando: {working_buttons}")
        print(f"Botoes com problema: {problem_buttons}")
        
        return working_buttons, problem_buttons
        
    except ImportError:
        print("Modulo 'config' nao encontrado")
        return [], []


# === Exemplo de Uso ===
if __name__ == "__main__":
    # Mini demo simples dos botões usando config.py
    print("Mini Demo Button - Estados (usando config.py)")
    
    try:
        # Importa configurações do BitDogLab V7
        from config import PINS
        
        # Cria botões A e B usando configurações do config.py
        button_a = Button(pin=PINS.BUTTON_A, pull_up=True, active_low=True)  # GPIO5 = Botão A
        button_b = Button(pin=PINS.BUTTON_B, pull_up=True, active_low=True)  # GPIO6 = Botão B
        
        print(f"Botao A: GPIO{PINS.BUTTON_A} - {button_a}")
        print(f"Botao B: GPIO{PINS.BUTTON_B} - {button_b}")
        print("Pressione os botoes para ver os estados!")
        print("Ctrl+C para sair")
        
        while True:
            # Lê estados dos botões
            state_a = button_a.read()
            state_b = button_b.read()
            
            # Mostra apenas quando há mudança de estado
            if state_a != ButtonState.UNCHANGED:
                print(f"[A] {state_a}")
                
            if state_b != ButtonState.UNCHANGED:
                print(f"[B] {state_b}")
            
            time.sleep_ms(50)
            
    except ImportError as e:
        print(f"Modulo nao encontrado ({e}) - usando valores fixos:")
        # Fallback para valores hardcoded se config.py não existir
        button_a = Button(pin=5, pull_up=True, active_low=True)  # GPIO5 = Botão A
        button_b = Button(pin=6, pull_up=True, active_low=True)  # GPIO6 = Botão B
        print("Botao A: GPIO5 (fallback)")
        print("Botao B: GPIO6 (fallback)")
        print("Pressione os botoes para ver os estados!")
        
        while True:
            state_a = button_a.read()
            state_b = button_b.read()
            
            if state_a != ButtonState.UNCHANGED:
                print(f"[A] {state_a}")
                
            if state_b != ButtonState.UNCHANGED:
                print(f"[B] {state_b}")
            
            time.sleep_ms(50)
            
    except KeyboardInterrupt:
        print("\nDemo finalizada!")
    except Exception as e:
        print(f"Erro: {e}")
