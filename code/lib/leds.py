import neopixel
from machine import Pin, PWM
from time import sleep

# Importa configurações do BitDogLab V7
try:
    from config import PINS, HARDWARE
except ImportError:
    # Fallback se config.py não disponível
    class FallbackConfig:
        NEOPIXEL = 7
        LED_RED = 13
        LED_GREEN = 11
        LED_BLUE = 12
        
    class FallbackHardware:
        NEOPIXEL_COUNT = 25
        NEOPIXEL_MATRIX_SIZE = (5, 5)
        PWM_FREQUENCY = 1000
        
    PINS = FallbackConfig()
    HARDWARE = FallbackHardware()

# =============================================================================
# CORES PADRÃO PARA NEOPIXEL (RGB)
# =============================================================================

# Cores básicas (brilho máximo - luminosidade controlada pelo brightness)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

# Cores adicionais
LIME = (0, 255, 0)
NAVY = (0, 0, 128)
TEAL = (0, 128, 128)
SILVER = (192, 192, 192)
MAROON = (128, 0, 0)
OLIVE = (128, 128, 0)
AQUA = (0, 255, 255)
FUCHSIA = (255, 0, 255)

# Lista de cores para uso em animações
COLORS = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE, ORANGE, PURPLE, PINK]

# Brilho global padrão
DEFAULT_BRIGHTNESS = 0.15

# =============================================================================
# CLASSE BASE LED - IMPLEMENTA DRY
# =============================================================================

class LED:
    """
    Classe base para todos os tipos de LED
    Implementa funcionalidades comuns seguindo o princípio DRY
    """
    
    def __init__(self, brightness=DEFAULT_BRIGHTNESS):
        """
        Inicializa LED base
        
        Args:
            brightness: Brilho padrão (0.0 a 1.0)
        """
        self.brightness = max(0.0, min(1.0, brightness))
        self._debug = False
    
    def set_debug(self, enabled):
        """Ativa/desativa modo debug"""
        self._debug = enabled
        if enabled:
            print(f"{self.__class__.__name__} Debug: {self}")
    
    def set_brightness(self, brightness):
        """Define o brilho padrão (0.0 a 1.0)"""
        self.brightness = max(0.0, min(1.0, brightness))
        if self._debug:
            print(f"Brilho alterado para: {self.brightness}")
    
    def _apply_brightness(self, color, brightness=None):
        """
        Aplica brilho a uma cor RGB
        
        Args:
            color: Tupla RGB (r, g, b)
            brightness: Brilho específico (usa padrão se None)
            
        Returns:
            Tupla RGB com brilho aplicado
        """
        brightness = brightness or self.brightness
        return tuple(int(c * brightness) for c in color)
    
    def _validate_color(self, color):
        """
        Valida se a cor está no formato correto
        
        Args:
            color: Tupla RGB para validar
            
        Returns:
            bool: True se válida
        """
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            return False
        return all(isinstance(c, int) and 0 <= c <= 255 for c in color)
    
    def off(self):
        """Desliga o LED - método abstrato"""
        raise NotImplementedError("Subclasses devem implementar off()")
    
    def set_color(self, color, brightness=None):
        """Define cor - método abstrato"""
        raise NotImplementedError("Subclasses devem implementar set_color()")
    
    def get_info(self):
        """Retorna informações básicas do LED"""
        return {
            "type": self.__class__.__name__,
            "brightness": self.brightness,
            "debug": self._debug
        }
    
    # Métodos de conveniência para cores comuns
    def red(self, brightness=None):
        """Define cor vermelha"""
        self.set_color(RED, brightness)
    
    def green(self, brightness=None):
        """Define cor verde"""
        self.set_color(GREEN, brightness)
    
    def blue(self, brightness=None):
        """Define cor azul"""
        self.set_color(BLUE, brightness)
    
    def white(self, brightness=None):
        """Define cor branca"""
        self.set_color(WHITE, brightness)
    
    def yellow(self, brightness=None):
        """Define cor amarela"""
        self.set_color(YELLOW, brightness)
    
    def cyan(self, brightness=None):
        """Define cor ciano"""
        self.set_color(CYAN, brightness)
    
    def magenta(self, brightness=None):
        """Define cor magenta"""
        self.set_color(MAGENTA, brightness)
    
    def orange(self, brightness=None):
        """Define cor laranja"""
        self.set_color(ORANGE, brightness)
    
    def purple(self, brightness=None):
        """Define cor roxa"""
        self.set_color(PURPLE, brightness)
    
    def pink(self, brightness=None):
        """Define cor rosa"""
        self.set_color(PINK, brightness)

# =============================================================================
# CLASSE LEDMATRIX - HERDA DE LED
# =============================================================================

class LEDMatrix(LED):
    """
    Classe para controle de matriz de LEDs NeoPixel WS2812B
    Herda de LED para reutilizar funcionalidades comuns (DRY)
    
    Auto-configuração: Usa config.py automaticamente para BitDogLab V7
    Configuração manual: LEDMatrix(pin=7, num_leds=25, width=5, height=5)
    """
    
    def __init__(self, pin=None, num_leds=None, width=None, height=None, brightness=DEFAULT_BRIGHTNESS):
        """
        Inicializa matriz LED (auto-configuração via config.py)
        
        Args:
            pin: GPIO da matriz (usa PINS.NEOPIXEL se None)
            num_leds: Número de LEDs (usa HARDWARE.NEOPIXEL_COUNT se None)
            width: Largura (usa HARDWARE.NEOPIXEL_MATRIX_SIZE[0] se None)
            height: Altura (usa HARDWARE.NEOPIXEL_MATRIX_SIZE[1] se None)
            brightness: Brilho padrão (0.0 a 1.0)
        """
        # Inicializa classe base
        super().__init__(brightness)
        
        # Auto-configuração via config.py
        self.pin_number = pin if pin is not None else PINS.NEOPIXEL
        self.num_leds = num_leds if num_leds is not None else HARDWARE.NEOPIXEL_COUNT
        
        if width is None or height is None:
            self.width, self.height = HARDWARE.NEOPIXEL_MATRIX_SIZE
        else:
            self.width = width
            self.height = height
        
        # Valida se as dimensões fazem sentido
        if self.width * self.height != self.num_leds:
            raise ValueError(f"Dimensões {self.width}x{self.height} não correspondem a {self.num_leds} LEDs")
        
        # Inicializa NeoPixel
        self.np = neopixel.NeoPixel(Pin(self.pin_number), self.num_leds)
        
        # Cache para padrões carregados
        self._pattern_cache = {}
        
        # Debug inicial
        if self._debug:
            print(f"LEDMatrix: GPIO{self.pin_number}, {self.width}x{self.height} ({self.num_leds} LEDs)")

    def set_pattern(self, pattern_name, color=WHITE, brightness=None):
        """
        Define um padrão na matriz a partir de um arquivo em assets/patterns/
        
        Args:
            pattern_name: Nome do padrão (sem extensão .txt)
            color: Cor para aplicar (padrão: branco)
            brightness: Brilho (usa padrão da matriz se None)
        """
        # Carrega padrão do cache ou arquivo
        pattern_coords = self._load_pattern(pattern_name)
        
        if pattern_coords:
            # Aplica padrão carregado
            for coord in pattern_coords:
                if len(coord) == 3:  # (x, y, cor) - padrão colorido
                    x, y, pattern_color = coord
                    self.set_led((x, y), pattern_color, brightness)
                elif len(coord) == 2:  # (x, y) - padrão simples
                    x, y = coord
                    self.set_led((x, y), color, brightness)
        elif self._debug:
            print(f"Padrão '{pattern_name}' não encontrado")
    
    def _load_pattern(self, pattern_name):
        """
        Carrega padrão de arquivo em assets/patterns/ (com cache)
        
        Args:
            pattern_name: Nome do arquivo (sem extensão)
            
        Returns:
            Lista de coordenadas: [(x,y), ...] ou [(x,y,cor), ...]
        """
        # Verifica cache primeiro
        if pattern_name in self._pattern_cache:
            return self._pattern_cache[pattern_name]
        
        # Adiciona extensão .txt se necessário
        filename = pattern_name if pattern_name.endswith('.txt') else pattern_name + '.txt'
        
        # Caminhos para buscar o arquivo
        possible_paths = [
            f"assets/patterns/{filename}",
            f"../assets/patterns/{filename}",
            f"../../assets/patterns/{filename}"
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r') as file:
                    content = file.read()
                
                # Faz o parsing do conteúdo
                pattern_coords = self._parse_pattern_content(content)
                
                # Armazena no cache
                self._pattern_cache[pattern_name] = pattern_coords
                
                if self._debug:
                    print(f"Padrão '{pattern_name}' carregado de {path}")
                
                return pattern_coords
                
            except OSError:
                continue  # Tenta próximo caminho
        
        if self._debug:
            print(f"Arquivo '{filename}' não encontrado nos caminhos de assets")
        
        return None

    def _parse_pattern_content(self, content):
        """
        Faz o parsing do conteúdo de um arquivo de padrão
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Lista de coordenadas: [(x,y), ...] para simples ou [(x,y,cor), ...] para coloridos
        """
        lines = content.split('\n')
        pattern_coords = []
        color_map = {}
        
        # Primeiro, processa definições de cores se existirem
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and ':' in line and '(' in line:
                # Formato: # 1: (255, 0, 0)
                try:
                    parts = line[2:].split(':', 1)  # Remove "# " e divide
                    color_num = parts[0].strip()
                    rgb_str = parts[1].strip()
                    
                    # Extrai valores RGB da string "(r, g, b)"
                    if '(' in rgb_str and ')' in rgb_str:
                        rgb_values = rgb_str.split('(')[1].split(')')[0]
                        r, g, b = [int(x.strip()) for x in rgb_values.split(',')]
                        color_map[color_num] = (r, g, b)
                except (ValueError, IndexError):
                    pass  # Ignora linhas mal formatadas
        
        # Debug das cores carregadas
        if self._debug and color_map:
            print(f"Cores carregadas: {color_map}")
        
        # Depois, processa o padrão visual - apenas linhas que são padrões válidos
        pattern_y = 0  # Contador separado para coordenadas Y do padrão
        for line in lines:
            line = line.strip()
            # Verifica se é uma linha de padrão válida (não comentário, não vazia, contém apenas caracteres de padrão)
            if (line and 
                not line.startswith('#') and 
                all(c in '.0123456789Xx ' for c in line) and
                any(c in '123456789Xx' for c in line)):  # Deve ter pelo menos um LED
                
                if self._debug:
                    print(f"Processando linha padrão Y={pattern_y}: '{line}'")
                
                for x, char in enumerate(line):
                    if char.upper() == 'X':  # Formato simples (X = LED aceso)
                        if pattern_y < self.height and x < self.width:  # Valida limites
                            pattern_coords.append((x, pattern_y))
                        elif self._debug:
                            print(f"Coordenada X fora dos limites: ({x}, {pattern_y})")
                    elif char.isdigit() and char != '0':  # Formato colorido (1-9)
                        if pattern_y < self.height and x < self.width:  # Valida limites
                            color = color_map.get(char, WHITE)  # Branco se cor não definida
                            pattern_coords.append((x, pattern_y, color))
                        elif self._debug:
                            print(f"Coordenada colorida fora dos limites: ({x}, {pattern_y})")
                
                pattern_y += 1  # Incrementa apenas para linhas válidas de padrão
                
                # Para de processar se já temos linhas suficientes para a matriz
                if pattern_y >= self.height:
                    break
        
        if self._debug:
            print(f"Padrão processado: {len(pattern_coords)} coordenadas")
        
        return pattern_coords

    def set_led(self, coord, color, brightness=None):
        """Define a cor de um LED específico"""
        x, y = coord
        
        # Valida coordenadas
        if not (0 <= x < self.width and 0 <= y < self.height):
            if self._debug:
                print(f"Coordenada ({x}, {y}) fora dos limites da matriz {self.width}x{self.height}")
            return

        # Linearização em serpentina (padrão BitDogLab)
        if y % 2 == 0:  # linha par (esquerda -> direita)
            index = y * self.width + x
        else:           # linha ímpar (direita -> esquerda)
            index = y * self.width + (self.width - 1 - x)

        # Aplica cor com brilho (usando método da classe base)
        adjusted_color = self._apply_brightness(color, brightness)
        self.np[index] = adjusted_color
        
        if self._debug:
            print(f"LED ({x}, {y}) -> index {index} -> cor {adjusted_color}")

    def set_color(self, color, brightness=None):
        """Define todos os LEDs para a mesma cor (implementa método abstrato)"""
        adjusted_color = self._apply_brightness(color, brightness)
        self.np.fill(adjusted_color)
        if self._debug:
            print(f"Todos os LEDs: cor {adjusted_color}")
    
    def set_all(self, color, brightness=None):
        """Alias para set_color (compatibilidade)"""
        self.set_color(color, brightness)
        
    def draw(self):
        """Atualiza a exibição da matriz"""
        self.np.write()
    
    def clear(self):
        """Limpa todos os LEDs (preto)"""
        self.np.fill((0, 0, 0))
        self.np.write()
    
    def off(self):
        """Desliga todos os LEDs (implementa método abstrato)"""
        self.clear()
    
    def show_info(self):
        """Mostra informações de debug dos LEDs"""
        print(f"=== LEDMatrix Info ===")
        print(f"GPIO: {self.pin_number}")
        print(f"Dimensões: {self.width}x{self.height}")
        print(f"Total LEDs: {self.num_leds}")
        print(f"Brilho: {self.brightness}")
        print(f"Padrões em cache: {len(self._pattern_cache)}")
        
        if self._debug:
            print("Estados dos LEDs:")
            for i in range(self.num_leds):
                print(f"LED {i}: {self.np[i]}")
    
    def get_info(self):
        """Retorna informações de configuração da matriz"""
        info = super().get_info()
        info.update({
            "pin": self.pin_number,
            "width": self.width,
            "height": self.height,
            "num_leds": self.num_leds,
            "cached_patterns": list(self._pattern_cache.keys())
        })
        return info
    
    def __str__(self):
        """Representação em string da matriz"""
        return f"LEDMatrix(GPIO{self.pin_number}, {self.width}x{self.height}, {self.num_leds} LEDs)"


# =============================================================================
# CLASSE CENTRALRED - HERDA DE LED (LED RGB Central)
# =============================================================================

class CentralLED(LED):
    """
    Classe para controle do LED RGB central (catodo comum) da BitDogLab V7
    Herda de LED para reutilizar funcionalidades comuns (DRY)
    
    Auto-configuração: Usa config.py automaticamente para BitDogLab V7
    Configuração manual: CentralLED(pin_red=13, pin_green=11, pin_blue=12)
    """
    
    def __init__(self, pin_red=None, pin_green=None, pin_blue=None, brightness=DEFAULT_BRIGHTNESS, pwm_freq=None):
        """
        Inicializa LED RGB central (auto-configuração via config.py)
        
        Args:
            pin_red: GPIO do LED vermelho (usa PINS.LED_RED se None)
            pin_green: GPIO do LED verde (usa PINS.LED_GREEN se None)
            pin_blue: GPIO do LED azul (usa PINS.LED_BLUE se None)
            brightness: Brilho padrão (0.0 a 1.0)
            pwm_freq: Frequência PWM (usa HARDWARE.PWM_FREQUENCY se None)
        """
        # Inicializa classe base
        super().__init__(brightness)
        
        # Auto-configuração via config.py
        self.pin_red = pin_red if pin_red is not None else PINS.LED_RED
        self.pin_green = pin_green if pin_green is not None else PINS.LED_GREEN
        self.pin_blue = pin_blue if pin_blue is not None else PINS.LED_BLUE
        self.pwm_freq = pwm_freq if pwm_freq is not None else HARDWARE.PWM_FREQUENCY
        
        # Inicializa PWM para cada cor
        self.red_pwm = PWM(Pin(self.pin_red))
        self.green_pwm = PWM(Pin(self.pin_green))
        self.blue_pwm = PWM(Pin(self.pin_blue))
        
        # Define frequência PWM
        self.red_pwm.freq(self.pwm_freq)
        self.green_pwm.freq(self.pwm_freq)
        self.blue_pwm.freq(self.pwm_freq)
        
        # Desliga LEDs inicialmente
        self.off()
        
        # Debug inicial
        if self._debug:
            print(f"CentralLED: R=GPIO{self.pin_red}, G=GPIO{self.pin_green}, B=GPIO{self.pin_blue}")
    
    def set_color(self, color, brightness=None):
        """
        Define a cor do LED RGB (implementa método abstrato)
        
        Args:
            color: Tupla RGB (r, g, b) com valores 0-255
            brightness: Brilho específico (usa padrão se None)
        """
        if not self._validate_color(color):
            if self._debug:
                print(f"Cor inválida: {color}")
            return
        
        brightness = brightness or self.brightness
        r, g, b = color
        
        # Aplica brilho e converte para duty_u16 (0-65535)
        r_duty = int((r / 255.0) * brightness * 65535)
        g_duty = int((g / 255.0) * brightness * 65535)
        b_duty = int((b / 255.0) * brightness * 65535)
        
        # Define duty cycle para cada cor
        self.red_pwm.duty_u16(r_duty)
        self.green_pwm.duty_u16(g_duty)
        self.blue_pwm.duty_u16(b_duty)
        
        if self._debug:
            print(f"LED Central: RGB({r}, {g}, {b}) -> duty({r_duty}, {g_duty}, {b_duty})")
    
    def off(self):
        """Desliga o LED (implementa método abstrato)"""
        self.red_pwm.duty_u16(0)
        self.green_pwm.duty_u16(0)
        self.blue_pwm.duty_u16(0)
        if self._debug:
            print("LED Central: OFF")
    
    def flash(self, color, times=3, delay=0.5, brightness=None):
        """
        Pisca o LED com uma cor específica
        
        Args:
            color: Cor para piscar
            times: Número de piscadas
            delay: Tempo entre piscadas
            brightness: Brilho específico
        """
        for _ in range(times):
            self.set_color(color, brightness)
            sleep(delay)
            self.off()
            sleep(delay)
    
    def get_info(self):
        """Retorna informações do LED central"""
        info = super().get_info()
        info.update({
            "pin_red": self.pin_red,
            "pin_green": self.pin_green,
            "pin_blue": self.pin_blue,
            "pwm_freq": self.pwm_freq
        })
        return info
    
    def __str__(self):
        """Representação em string do LED central"""
        return f"CentralLED(R=GPIO{self.pin_red}, G=GPIO{self.pin_green}, B=GPIO{self.pin_blue})"

# =============================================================================
# EXEMPLO DE USO - ARQUITETURA DRY COM HERANÇA
# =============================================================================

if __name__ == "__main__":
    print("🎯 Demo Sistema LEDs DRY - BitDogLab V7")
    print("Arquitetura: LED (base) -> LEDMatrix + CentralLED")
    
    try:
        # Cria componentes com auto-configuração (config.py)
        print("\n📋 Criando componentes...")
        matrix = LEDMatrix(brightness=0.15)      # Auto-configura via PINS.NEOPIXEL
        central = CentralLED(brightness=0.15)    # Auto-configura via PINS.LED_*
        
        matrix.set_debug(True)
        central.set_debug(True)
        
        print(f"✅ Matriz criada: {matrix}")
        print(f"✅ LED Central criado: {central}")
        
        print("\n🧪 Iniciando testes DRY...")
        
        # Teste 1: Métodos herdados da classe base LED
        print("\n1. 🎨 Teste métodos herdados (DRY)")
        central.set_color(RED, 0.5)
        sleep(1)
        central.set_color(GREEN, 0.5)
        sleep(1)
        central.set_color(BLUE, 0.5)
        sleep(1)
        central.off()
        
        # Teste 2: Matriz usando métodos da base
        print("\n2. 🟩 Teste matriz com herança")
        matrix.set_color(WHITE, 0.3)
        matrix.draw()
        sleep(1)
        matrix.off()
        
        # Teste 3: Controle independente com DRY
        print("\n3. 🚀 Controle independente DRY")
        central.set_color(YELLOW, 0.4)
        matrix.set_color(BLUE, 0.1)
        matrix.draw()
        sleep(1.5)
        
        # Desliga tudo usando métodos unificados
        central.off()
        matrix.off()
        
        # Teste 4: Padrão na matriz + LED central
        print("\n4. 📐 Padrão + LED central coordenados")
        central.set_color(GREEN, 0.3)
        matrix.set_pattern("heart_color")
        matrix.draw()
        sleep(2)
        
        # Teste 5: Flash independente com herança
        print("\n5. ⚡ Flash com métodos unificados")
        central.flash(MAGENTA, times=3, delay=0.3)
        matrix.set_color(CYAN, 0.1)
        matrix.draw()
        sleep(1)
        matrix.off()
        
        # Teste 6: Demonstração do DRY
        print("\n6. 🔧 Demonstração DRY - Métodos comuns")
        
        # Ambos têm os mesmos métodos da classe base
        components = [matrix, central]
        colors_test = [RED, GREEN, BLUE]
        
        for i, comp in enumerate(components):
            print(f"   Testando {comp.__class__.__name__}...")
            comp.set_brightness(0.2)
            for color in colors_test:
                comp.set_color(color, 0.15)
                if hasattr(comp, 'draw'):
                    comp.draw()
                sleep(0.3)
            comp.off()
        
        print("\n✨ Demo concluída com sucesso!")
        print("\n📊 Informações dos componentes:")
        print(f"Matrix Info: {matrix.get_info()}")
        print(f"Central Info: {central.get_info()}")
        
    except ImportError as e:
        print(f"\n⚠️  Config.py não encontrado ({e}) - usando configuração manual:")
        
        # Demo com configuração manual (sem config.py)
        print("🔧 Executando demo com parâmetros manuais...")
        matrix = LEDMatrix(pin=7, num_leds=25, width=5, height=5, brightness=0.15)
        central = CentralLED(pin_red=13, pin_green=11, pin_blue=12, brightness=0.15)
        
        # Teste simples DRY
        print("🎨 Teste herança - cores básicas...")
        central.set_color(RED, 0.3)
        sleep(1)
        central.off()
        
        print("🟩 Teste matriz centro...")
        matrix.set_led((2, 2), WHITE, 0.2)
        matrix.draw()
        sleep(1)
        matrix.clear()
        
        print("✅ Demo manual concluída!")
        
    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        import traceback
        traceback.print_exc()
