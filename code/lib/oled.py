"""
Módulo OLED Genérico - BitDogLab V7
Baseado nos exemplos funcionais da pasta display-OLED
Auto-configuração via config.py com fallback
"""

from machine import Pin, SoftI2C
from time import sleep

# Importa driver SSD1306 primeiro
try:
    from ssd1306 import SSD1306_I2C
    SSD1306_AVAILABLE = True
except ImportError:
    SSD1306_AVAILABLE = False

# Importa configurações do BitDogLab V7
try:
    from config import PINS, HARDWARE, SOFTWARE
except ImportError:
    # Fallback se config.py não disponível
    class FallbackPins:
        # Usando pinos que funcionam nos exemplos
        OLED_SDA = 14        # GPIO14 (funciona nos exemplos)
        OLED_SCL = 15        # GPIO15 (funciona nos exemplos)
        OLED_ADDRESS = 0x3C
        
    class FallbackHardware:
        DISPLAY_WIDTH = 128
        DISPLAY_HEIGHT = 64
        DISPLAY_LINE_HEIGHT = 8
        
    class FallbackSoftware:
        DEBUG_MODE = True
        
    PINS = FallbackPins()
    HARDWARE = FallbackHardware()
    SOFTWARE = FallbackSoftware()

# Configurações funcionais baseadas nos exemplos
# IMPORTANTE: Os exemplos usam GPIO14 (SDA) e GPIO15 (SCL)
I2C_SDA_PIN = 14  # GPIO14 - igual aos exemplos funcionais
I2C_SCL_PIN = 15  # GPIO15 - igual aos exemplos funcionais

# Debug de driver após importar config
if not SSD1306_AVAILABLE and SOFTWARE.DEBUG_MODE:
    print("OLED: Driver SSD1306 não encontrado - modo simulação")

class OLEDDisplay:
    """
    Classe genérica para controle de display OLED SSD1306
    Baseada nos exemplos funcionais da BitDogLab V7
    
    Configuração automática: OLEDDisplay()
    Configuração manual: OLEDDisplay(width=128, height=64, sda=14, scl=15)
    """
    
    def __init__(self, width=None, height=None, sda=None, scl=None, address=None, line_height=None):
        """
        Inicializa display OLED (baseado nos exemplos funcionais)
        
        Args:
            width: Largura do display (padrão: 128)
            height: Altura do display (padrão: 64)
            sda: Pino SDA (padrão: GPIO14 - igual exemplos)
            scl: Pino SCL (padrão: GPIO15 - igual exemplos)
            address: Endereço I2C (padrão: 0x3C)
            line_height: Altura da linha (padrão: 8)
        """
        # Configurações baseadas nos exemplos funcionais
        self.width = width if width is not None else 128
        self.height = height if height is not None else 64
        self.line_height = line_height if line_height is not None else 8
        
        # Usa pinos dos exemplos funcionais por padrão
        self.sda_pin = sda if sda is not None else I2C_SDA_PIN  # GPIO14
        self.scl_pin = scl if scl is not None else I2C_SCL_PIN  # GPIO15
        self.i2c_address = address if address is not None else 0x3C
        
        # Flag para controle
        self.is_present = False
        self.oled = None
        self._debug = SOFTWARE.DEBUG_MODE if hasattr(SOFTWARE, 'DEBUG_MODE') else False
        
        # Inicializa display
        self._init_display()
    
    def _init_display(self):
        """Inicializa o display OLED (padrão dos exemplos funcionais)"""
        if not SSD1306_AVAILABLE:
            if self._debug:
                print("OLED: Driver SSD1306 não disponível - modo simulação")
            return
        
        try:
            # Padrão exato dos exemplos funcionais
            # i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
            i2c = SoftI2C(scl=Pin(self.scl_pin), sda=Pin(self.sda_pin))
            
            if self._debug:
                print(f'OLED: Inicializando - SDA=GPIO{self.sda_pin}, SCL=GPIO{self.scl_pin}')
            
            # Inicializa display exatamente como nos exemplos
            self.oled = SSD1306_I2C(self.width, self.height, i2c)
            self.is_present = True
            
            # Teste inicial - igual aos exemplos
            self.oled.fill(0)
            self.oled.show()
            
            if self._debug:
                print(f'OLED: Display funcionando {self.width}x{self.height}')
                print(f'OLED: Padrão dos exemplos - SDA={self.sda_pin}, SCL={self.scl_pin}')
                
        except Exception as e:
            self.is_present = False
            if self._debug:
                print(f'OLED: Falha na inicialização - {e}')
                print(f'OLED: Tentou SDA=GPIO{self.sda_pin}, SCL=GPIO{self.scl_pin}')
                print('OLED: Verifique se ssd1306.py está instalado')

    def set_debug(self, enabled):
        """Ativa/desativa modo debug"""
        self._debug = enabled
        if enabled:
            print(f"OLEDDisplay Debug: {self}")

    def clear(self):
        """Limpa a tela (igual aos exemplos)"""
        if self.is_present and self.oled is not None:
            self.oled.fill(0)
            self.oled.show()
        elif self._debug:
            print("OLED: clear() - simulado")
    
    def show(self):
        """Atualiza o display (igual aos exemplos)"""
        if self.is_present and self.oled is not None:
            self.oled.show()
        elif self._debug:
            print("OLED: show() - simulado")

    def text(self, text, x=0, y=0):
        """Desenha texto em posição específica (igual aos exemplos)"""
        if self.is_present and self.oled is not None:
            self.oled.text(str(text), x, y)
        elif self._debug:
            print(f"OLED: text('{text}', {x}, {y}) - simulado")

    def draw_text(self, text, x=0, y=0, align='left'):
        """Desenha texto com alinhamento"""
        if align == 'center':
            x = max((self.width - len(str(text)) * 8) // 2, 0)
        elif align == 'right':
            x = max(self.width - len(str(text)) * 8, 0)
        
        self.text(text, x, y)

    def draw_lines(self, lines, valign='top', global_align='left'):
        """
        Desenha múltiplas linhas de texto
        
        Args:
            lines: Lista de strings ou dicts {'text': str, 'align': str}
            valign: Alinhamento vertical 'top', 'middle', 'bottom'
            global_align: Alinhamento padrão 'left', 'center', 'right'
        """
        self.clear()
        
        # Converte strings simples para formato dict
        formatted_lines = []
        for line in lines:
            if isinstance(line, str):
                formatted_lines.append({'text': line, 'align': global_align})
            else:
                formatted_lines.append(line)
        
        # Calcula posição Y inicial
        total_height = len(formatted_lines) * self.line_height
        if valign == 'top':
            y_offset = 0
        elif valign == 'middle':
            y_offset = max((self.height - total_height) // 2, 0)
        elif valign == 'bottom':
            y_offset = max(self.height - total_height, 0)
        else:
            y_offset = 0

        # Desenha cada linha
        for i, line_data in enumerate(formatted_lines):
            text = line_data.get('text', '')
            align = line_data.get('align', global_align)
            y = y_offset + i * self.line_height
            
            self.draw_text(text, 0, y, align)

        self.show()
    
    def fill(self, color):
        """Preenche a tela com cor (0=preto, 1=branco)"""
        if self.is_present and self.oled is not None:
            self.oled.fill(color)
        elif self._debug:
            print(f"OLED: fill({color}) - simulado")
    
    def pixel(self, x, y, color):
        """Define cor de um pixel"""
        if self.is_present and self.oled is not None:
            self.oled.pixel(x, y, color)
        elif self._debug:
            print(f"OLED: pixel({x}, {y}, {color}) - simulado")
    
    def line(self, x1, y1, x2, y2, color):
        """Desenha linha"""
        if self.is_present and self.oled is not None:
            self.oled.line(x1, y1, x2, y2, color)
        elif self._debug:
            print(f"OLED: line({x1}, {y1}, {x2}, {y2}, {color}) - simulado")
    
    def rect(self, x, y, w, h, color, fill=False):
        """Desenha retângulo"""
        if self.is_present and self.oled is not None:
            if fill:
                self.oled.fill_rect(x, y, w, h, color)
            else:
                self.oled.rect(x, y, w, h, color)
        elif self._debug:
            action = "fill_rect" if fill else "rect"
            print(f"OLED: {action}({x}, {y}, {w}, {h}, {color}) - simulado")
    
    def get_info(self):
        """Retorna informações do display"""
        return {
            "type": "OLEDDisplay",
            "width": self.width,
            "height": self.height,
            "line_height": self.line_height,
            "sda_pin": self.sda_pin,
            "scl_pin": self.scl_pin,
            "i2c_address": self.i2c_address,
            "is_present": self.is_present,
            "debug": self._debug,
            "based_on_examples": True  # Indica que segue padrão dos exemplos
        }
    
    def __str__(self):
        """Representação em string do display"""
        status = "conectado" if self.is_present else "simulado"
        return f"OLEDDisplay({self.width}x{self.height}, SDA={self.sda_pin}, SCL={self.scl_pin}, {status})"


# =====================================================================
# MINI TESTE - Execute: import oled; oled.mini_teste()
# =====================================================================

def mini_teste():
    """Mini teste da classe OLEDDisplay"""
    print("\n=== Mini Teste OLEDDisplay ===")
    
    # Teste 1: Instanciação automática
    print("1. Criando display com configuração dos exemplos...")
    display = OLEDDisplay()
    print(f"   Resultado: {display}")
    print(f"   Info: {display.get_info()}")
    
    # Teste 2: Ativando debug
    print("\n2. Testando modo debug...")
    display.set_debug(True)
    
    # Teste 3: Testando métodos básicos (igual aos exemplos)
    print("\n3. Testando métodos básicos...")
    display.clear()
    display.text("BitDogLab V7", 0, 0)
    display.text("OLED Test", 0, 10)
    display.show()
    
    # Teste 4: Testando desenho de linhas
    print("\n4. Testando draw_lines...")
    lines = [
        "BitDogLab V7",
        {"text": "Centro", "align": "center"},
        {"text": "Direita", "align": "right"}
    ]
    display.draw_lines(lines, valign='middle')
    
    # Teste 5: Testando desenho básico
    print("\n5. Testando desenho básico...")
    display.clear()
    display.pixel(10, 10, 1)
    display.line(0, 0, 20, 20, 1)
    display.rect(30, 10, 20, 15, 1)
    display.rect(60, 10, 20, 15, 1, fill=True)
    display.show()
    
    print("\n=== Teste Concluído ===")
    return display

if __name__ == "__main__":
    # Teste direto OLED - Padrão dos Exemplos Funcionais
    print("🎯 Demo OLED - BitDogLab V7 (Baseado nos Exemplos)")
    print(f"Configuração: GPIO{I2C_SDA_PIN} (SDA), GPIO{I2C_SCL_PIN} (SCL), 0x3C")
    
    try:
        # Cria display usando configuração dos exemplos
        print("\n1. Criando display...")
        display = OLEDDisplay()
        print(f"   Resultado: {display}")
        
        if display.is_present:
            print("\n2. ✅ OLED conectado - testando...")
            
            # Teste igual ao exemplo Ola_Mundo.py
            print("   - Teste 'Olá Mundo' (igual exemplo)...")
            display.clear()
            display.text("Ola, Mundo!", 20, 28)  # Igual ao exemplo
            display.show()
            print("   - Texto exibido na tela!")
            
            # Aguarda um pouco
            sleep(2)
            
            # Teste de alinhamento personalizado
            print("   - Testando alinhamentos...")
            lines = [
                "BitDogLab V7",
                {"text": "Funcionando!", "align": "center"},
                {"text": "Exemplos OK", "align": "right"}
            ]
            display.draw_lines(lines, valign='middle')
            print("   - Alinhamentos aplicados!")
            
            print("\n🎉 OLED funcionando com padrão dos exemplos!")
            
        else:
            print("\n⚠️  OLED não detectado")
            print("Verifique:")
            print(f"  - Pinos: SDA=GPIO{I2C_SDA_PIN}, SCL=GPIO{I2C_SCL_PIN}")
            print("  - Driver ssd1306.py instalado")
            print("  - Conexões físicas do display")
            
            # Teste simulado
            display.set_debug(True)
            display.clear()
            display.text("Teste simulado", 0, 0)
            display.show()
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("Verifique se o hardware OLED está conectado corretamente")
    
    print("\n=== Demo Finalizada ===")
    
    # Executa mini teste adicional se necessário
    if SSD1306_AVAILABLE:
        mini_teste()

# Alias para compatibilidade com versão anterior
OledScreen = OLEDDisplay
