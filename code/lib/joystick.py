"""
Classe Joystick Genérica para MicroPython
Suporta qualquer joystick analógico com 2 eixos (X, Y) e botão opcional
Compatível com joysticks tipo KY-023 e similares
"""

from machine import ADC, Pin
import time

# Direções como strings (constante global)
DIRECTIONS = (
    "center", "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest"
)

class Joystick:
    """
    Classe genérica para controle de joystick analógico
    
    Parâmetros:
    - pin_x: GPIO para eixo X (analógico)
    - pin_y: GPIO para eixo Y (analógico) 
    - pin_btn: GPIO para botão (digital, opcional)
    - deadzone_x: Zona morta para eixo X (0-65535)
    - deadzone_y: Zona morta para eixo Y (0-65535)
    - invert_x: Inverte direção do eixo X
    - invert_y: Inverte direção do eixo Y
    """
    
    def __init__(self, pin_x, pin_y, pin_btn=None, deadzone_x=5000, deadzone_y=5000, 
                 invert_x=False, invert_y=False):
        # Configuração dos pinos
        self.pin_x = pin_x
        self.pin_y = pin_y
        self.pin_btn = pin_btn
        
        # Inicialização do hardware
        self.x = ADC(pin_x)
        self.y = ADC(pin_y)
        self.btn = Pin(pin_btn, Pin.IN, Pin.PULL_UP) if pin_btn is not None else None

        # Configurações de comportamento
        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y
        self.invert_x = invert_x
        self.invert_y = invert_y

        # Calibração inicial automática
        self.center_x = self.x.read_u16()
        self.center_y = self.y.read_u16()

        # Sistema de callbacks
        self._btn_callback = None
        self._last_btn_state = self.is_pressed()
        
        # Flag para debug
        self._debug = False

    # === Métodos de Configuração ===
    
    def set_debug(self, enabled):
        """Ativa/desativa modo debug"""
        self._debug = enabled
        if enabled:
            print(f"Joystick Debug: Pinos X={self.pin_x}, Y={self.pin_y}, Btn={self.pin_btn}")
            print(f"Centro: X={self.center_x}, Y={self.center_y}")
    
    def set_deadzone(self, deadzone_x, deadzone_y=None):
        """Define zona morta para os eixos"""
        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y if deadzone_y is not None else deadzone_x
        if self._debug:
            print(f"Zona morta atualizada: X={self.deadzone_x}, Y={self.deadzone_y}")
    
    def set_inversion(self, invert_x=None, invert_y=None):
        """Define inversão dos eixos"""
        if invert_x is not None:
            self.invert_x = invert_x
        if invert_y is not None:
            self.invert_y = invert_y
        if self._debug:
            print(f"Inversão: X={self.invert_x}, Y={self.invert_y}")

    # === Leitura dos valores ===
    
    def read_raw(self):
        """Lê valores brutos do ADC (0-65535)"""
        return self.x.read_u16(), self.y.read_u16()

    def get_normalized(self):
        """Lê valores normalizados com zona morta (-1.0 a 1.0)"""
        raw_x, raw_y = self.read_raw()
        
        # Aplica inversão se configurada
        if self.invert_x:
            raw_x = 65535 - raw_x
        if self.invert_y:
            raw_y = 65535 - raw_y
        
        # Calcula normalização baseada no centro
        max_x = max(self.center_x, 65535 - self.center_x)
        max_y = max(self.center_y, 65535 - self.center_y)
        norm_x = (raw_x - self.center_x) / max_x if max_x != 0 else 0
        norm_y = (raw_y - self.center_y) / max_y if max_y != 0 else 0
        
        # Aplica zona morta
        if abs(norm_x) < self.deadzone_x / max_x:
            norm_x = 0
        if abs(norm_y) < self.deadzone_y / max_y:
            norm_y = 0
        
        # Limita valores entre -1.0 e 1.0
        norm_x = max(-1.0, min(1.0, norm_x))
        norm_y = max(-1.0, min(1.0, norm_y))
        
        return norm_x, norm_y

    def get_direction(self):
        """Determina a direção baseada na posição do joystick (9 direções)"""
        # Usa valores normalizados que já aplicam zona morta corretamente
        norm_x, norm_y = self.get_normalized()
        
        # Se ambos os valores estão próximos de zero, está no centro
        if abs(norm_x) < 0.3 and abs(norm_y) < 0.3:
            return "center"

        # Calcula ângulo usando valores normalizados
        import math
        angle = math.degrees(math.atan2(-norm_y, norm_x))  # -norm_y corrige norte/sul
        if angle < 0:
            angle += 360

        # Determina direção baseada no ângulo
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
    
    def get_angle(self):
        """Retorna o ângulo em graus (0-360)"""
        # Usa valores normalizados para consistência
        norm_x, norm_y = self.get_normalized()
        
        # Se ambos os valores estão próximos de zero, não há direção definida
        if abs(norm_x) < 0.3 and abs(norm_y) < 0.3:
            return None  # Sem direção definida
        
        import math
        angle = math.degrees(math.atan2(-norm_y, norm_x))  # -norm_y corrige norte/sul
        if angle < 0:
            angle += 360
        return angle
    
    def get_distance_from_center(self):
        """Retorna a distância do centro (0.0 a 1.0)"""
        norm_x, norm_y = self.get_normalized()
        import math
        return min(1.0, math.sqrt(norm_x**2 + norm_y**2))

    # === Controle do Botão ===
    
    def is_pressed(self):
        """Verifica se o botão está pressionado"""
        if self.btn is not None:
            return self.btn.value() == 0
        return False
    
    def wait_for_release(self, timeout=None):
        """Aguarda o botão ser liberado (com timeout opcional em segundos)"""
        if self.btn is None:
            return False
            
        start_time = time.ticks_ms()
        while self.is_pressed():
            if timeout and (time.ticks_diff(time.ticks_ms(), start_time) > timeout * 1000):
                return False
            time.sleep_ms(10)
        return True

    # === Calibração ===
    
    def calibrate(self, samples=100, show_progress=False):
        """
        Recalibra o centro do joystick
        
        Parâmetros:
        - samples: Número de amostras para média
        - show_progress: Mostra progresso da calibração
        """
        if show_progress:
            print("Calibrando joystick... Mantenha-o centralizado!")
        
        sum_x = 0
        sum_y = 0
        
        for i in range(samples):
            sum_x += self.x.read_u16()
            sum_y += self.y.read_u16()
            
            if show_progress and (i + 1) % 20 == 0:
                print(f"Progresso: {((i + 1) / samples) * 100:.0f}%")
            
            time.sleep_ms(10)
        
        self.center_x = sum_x // samples
        self.center_y = sum_y // samples
        
        if show_progress or self._debug:
            print(f"Calibração concluída: Centro X={self.center_x}, Y={self.center_y}")
    
    def reset_calibration(self):
        """Reseta calibração para o centro padrão (32768)"""
        self.center_x = 32768
        self.center_y = 32768
        if self._debug:
            print("Calibração resetada para centro padrão")

    # === Sistema de Callbacks ===
    
    def on_press(self, callback):
        """Define callback para quando o botão for pressionado"""
        self._btn_callback = callback
        if self._debug:
            print("Callback de pressionamento configurado")

    def check_button(self):
        """Verifica se o botão foi pressionado e executa callback se necessário"""
        if self._btn_callback is not None and self.btn is not None:
            current = self.is_pressed()
            if current and not self._last_btn_state:
                if self._debug:
                    print("Executando callback de pressionamento")
                self._btn_callback()
            self._last_btn_state = current

    # === Leitura Completa ===
    
    def read(self):
        """
        Leitura completa do joystick com todas as informações
        
        Retorna dicionário com:
        - raw: Valores brutos (x, y)
        - norm: Valores normalizados (x, y)
        - percent: Porcentagens (x, y)
        - dir: Direção como string
        - angle: Ângulo em graus (ou None se centralizado)
        - distance: Distância do centro (0.0-1.0)
        - pressed: Estado do botão
        """
        norm_x, norm_y = self.get_normalized()
        return {
            "raw": self.read_raw(),
            "norm": (norm_x, norm_y),
            "dir": self.get_direction(),
            "angle": self.get_angle(),
            "distance": self.get_distance_from_center(),
            "pressed": self.is_pressed()
        }
    
    def read_simple(self):
        """Leitura simples compatível com versão anterior"""
        norm_x, norm_y = self.get_normalized()
        return {
            "raw": self.read_raw(),
            "norm": (norm_x, norm_y),
            "dir": self.get_direction(),
            "pressed": self.is_pressed()
        }
    
    # === Métodos Utilitários ===
    
    def get_info(self):
        """Retorna informações de configuração do joystick"""
        return {
            "pins": {"x": self.pin_x, "y": self.pin_y, "btn": self.pin_btn},
            "center": {"x": self.center_x, "y": self.center_y},
            "deadzone": {"x": self.deadzone_x, "y": self.deadzone_y},
            "inversion": {"x": self.invert_x, "y": self.invert_y},
            "debug": self._debug
        }
    
    def __str__(self):
        """Representação em string do joystick"""
        info = self.get_info()
        return f"Joystick(X={info['pins']['x']}, Y={info['pins']['y']}, Btn={info['pins']['btn']})"


# === Exemplo de Uso ===
if __name__ == "__main__":
    # Exemplo básico de uso do joystick
    print("Demo Joystick Generico")
    
    try:
        # Importa configurações do BitDogLab
        from config import PINS
        
        # Cria joystick com configuração BitDogLab V7
        joystick = Joystick(
            pin_x=PINS.JOYSTICK_VRX,
            pin_y=PINS.JOYSTICK_VRY,
            pin_btn=PINS.JOYSTICK_BUTTON,
            deadzone_x=3000,  # Zona morta menor para melhor detecção do centro
            deadzone_y=3000,
            invert_y=True  # BitDogLab tem Y invertido
        )
        
        print(f"Joystick criado: {joystick}")
        print("Mova o joystick e pressione o botao!")
        print("Ctrl+C para sair")
        
        last_dir = ""
        while True:
            # Leitura simples
            data = joystick.read_simple()
            
            # Mostra direção quando muda
            if data["dir"] != last_dir:
                print(f"Direcao: {data['dir']} | Coord {data['norm']}")
                last_dir = data["dir"]
            
            # Mostra quando botão é pressionado
            if data["pressed"]:
                print("BOTAO pressionado!")
                joystick.wait_for_release()
            
            time.sleep_ms(100)
            
    except ImportError:
        print("Modulo 'config' nao encontrado")
        print("Para usar, configure os pinos manualmente:")
        print("joystick = Joystick(pin_x=27, pin_y=26, pin_btn=22)")
    except KeyboardInterrupt:
        print("\nDemo finalizada!")
    except Exception as e:
        print(f"Erro: {e}")