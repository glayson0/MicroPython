# =============================================================================
# CONFIGURAÇÕES DE PINOS GPIO - BITDOGLAB V7
# =============================================================================

class PinConfig:
    """Configurações de pinos GPIO do BitDogLab V7"""
    
    # DISPLAY OLED (I2C1)
    # IMPORTANTE: Exemplos funcionais usam GPIO14 (SDA) e GPIO15 (SCL)
    OLED_SDA = 14       # GPIO14 (SDA) - confirmado pelos exemplos funcionais
    OLED_SCL = 15       # GPIO15 (SCL) - confirmado pelos exemplos funcionais
    OLED_ADDRESS = 0x3C
    
    # BOTÕES (2 BOTÕES + JOYSTICK BUTTON)
    BUTTON_A = 5        # GPIO5  (Botão A, pull-up interno)
    BUTTON_B = 6        # GPIO6  (Botão B, pull-up interno)
    JOYSTICK_BUTTON = 22 # GPIO22 (Joystick SW, pull-up interno)
        
    # JOYSTICK ANALÓGICO KY023
    JOYSTICK_VRX = 27   # GPIO27 (VRx)
    JOYSTICK_VRY = 26   # GPIO26 (VRy)
    
    # AUDIO
    BUZZER = 21         # GPIO21 (Buzzer passivo via transistor)
    MICROPHONE = 28     # GPIO28 (Microfone eletreto analógico)
    
    # LEDs RGB (CATODO COMUM)
    LED_RED = 13        # GPIO13 (Vermelho, resistor 220Ω)
    LED_GREEN = 11      # GPIO11 (Verde, resistor 220Ω)
    LED_BLUE = 12       # GPIO12 (Azul, resistor 150Ω)
    
    # MATRIZ NEOPIXEL WS2812B 5x5
    NEOPIXEL = 7        # GPIO7 (Matriz 5x5 = 25 LEDs)
    
    # CONECTORES I2C
    I2C0_SDA = 0        # GPIO0 (Conector I2C 0 - direita)
    I2C0_SCL = 1        # GPIO1 (Conector I2C 0 - direita)
    I2C1_SDA = 2        # GPIO2 (Conector I2C 1 - esquerda)
    I2C1_SCL = 3        # GPIO3 (Conector I2C 1 - esquerda)
    
    # UART (pode usar I2C0)
    UART_TX = 0         # GPIO0 (TX quando usado como UART)
    UART_RX = 1         # GPIO1 (RX quando usado como UART)
    
    # BARRA DE TERMINAIS JACARÉ
    TERMINAL_DIG0 = 0   # GPIO0 (Terminal digital 0)
    TERMINAL_DIG1 = 1   # GPIO1 (Terminal digital 1)
    TERMINAL_DIG2 = 2   # GPIO2 (Terminal digital 2)
    TERMINAL_DIG3 = 3   # GPIO3 (Terminal digital 3)
    
    # CONECTOR IDC 14 PINOS (EXPANSÃO)
    IDC_PIN4 = 8        # GPIO8  (IDC pino 4)
    IDC_PIN5 = 28       # GPIO28 (IDC pino 5 - mesmo do microfone)
    IDC_PIN6 = 9        # GPIO9  (IDC pino 6)
    IDC_PIN8 = 4        # GPIO4  (IDC pino 8)
    IDC_PIN9 = 17       # GPIO17 (IDC pino 9)
    IDC_PIN11 = 16      # GPIO16 (IDC pino 11)
    IDC_PIN12 = 19      # GPIO19 (IDC pino 12)
    IDC_PIN14 = 18      # GPIO18 (IDC pino 14)
    
    # SPI (via conector IDC para expansões)
    SPI_RX = 16         # GPIO16 (SPI RX)
    SPI_CSN = 17        # GPIO17 (SPI CSn - Chip Select)
    SPI_SCK = 18        # GPIO18 (SPI SCK - Clock)
    SPI_TX = 19         # GPIO19 (SPI TX)
    
    # ALIASES PARA COMPATIBILIDADE
    I2C_SDA = I2C1_SDA  # Alias para código existente
    I2C_SCL = I2C1_SCL  # Alias para código existente

# =============================================================================
# CONFIGURAÇÕES DE HARDWARE
# =============================================================================

class HardwareConfig:
    """Configurações de hardware BitDogLab V7"""
    
    # DISPLAY OLED - SUPORTE A SSD1306 E SH1107
    # SSD1306 (tradicional)
    SSD1306_WIDTH = 128
    SSD1306_HEIGHT = 64
    
    # SH1107 (novidade V7)
    SH1107_WIDTH = 128
    SH1107_HEIGHT = 128
    
    # Configuração padrão (SSD1306 para compatibilidade)
    DISPLAY_WIDTH = SSD1306_WIDTH
    DISPLAY_HEIGHT = SSD1306_HEIGHT
    DISPLAY_CONTROLLER = 'ssd1306'
    DISPLAY_ADDRESS = 0x3C
    DISPLAY_LINE_HEIGHT = 8
    
    # NEOPIXEL LED MATRIX WS2812B
    NEOPIXEL_COUNT = 25
    NEOPIXEL_MATRIX_SIZE = (5, 5)
    NEOPIXEL_MATRIX = [
        [24, 23, 22, 21, 20],  # Linha 0
        [15, 16, 17, 18, 19],  # Linha 1
        [14, 13, 12, 11, 10],  # Linha 2
        [5,  6,  7,  8,  9],   # Linha 3
        [4,  3,  2,  1,  0]    # Linha 4
    ]
    
    # LED RGB (CATODO COMUM)
    LED_RED_RESISTOR = 220      # 220Ω
    LED_GREEN_RESISTOR = 220    # 220Ω
    LED_BLUE_RESISTOR = 150     # 150Ω
    LED_COMMON_CATHODE = True
    
    # PWM E FREQUÊNCIAS
    PWM_FREQUENCY = 1000
    BUZZER_DEFAULT_FREQ = 1000
    PWM_U16_MAX = 65535
    
    # ADC CONFIGURAÇÃO
    ADC_RESOLUTION = 65536      # 16-bit ADC
    ADC_VOLTAGE_REF = 3.3       # 3.3V reference
    MICROPHONE_OFFSET_VOLTAGE = 1.65  # 1.65V offset
    MICROPHONE_MIN_VOLTAGE = 0.0
    MICROPHONE_MAX_VOLTAGE = 3.3
    
    # JOYSTICK CALIBRAÇÃO
    JOYSTICK_MIN = 240
    JOYSTICK_MAX = 65279
    JOYSTICK_CENTER_OFFSET_X = 0
    JOYSTICK_CENTER_OFFSET_Y = 400
    
    # BOTÕES (PULL-UP INTERNO)
    BUTTON_PULL_UP = True
    BUTTON_ACTIVE_LOW = True    # LOW quando pressionado
    DEBOUNCE_TIME = 0.1
    
    # I2C CONFIGURAÇÃO
    I2C0_FREQ = 100000          # 100kHz para I2C 0
    I2C1_FREQ = 100000          # 100kHz para I2C 1 (OLED)
    I2C_CHANNEL_OLED = 1        # Canal I2C usado pelo OLED
    
    # SPI CONFIGURAÇÃO
    SPI_BAUDRATE = 1000000      # 1MHz
    SPI_POLARITY = 0
    SPI_PHASE = 0
    
    # TIMING E DELAYS
    DEFAULT_ANIMATION_DELAY = 0.1
    BOOT_DELAY = 0.5
    
    # VOLTAGENS E ALIMENTAÇÃO
    SUPPLY_3V3 = 3.3
    SUPPLY_5V = 5.0
    SUPPLY_TOLERANCE = 0.1      # ±10% tolerância

# =============================================================================
# CONFIGURAÇÕES DE SOFTWARE
# =============================================================================

class SoftwareConfig:
    """Configurações de software BitDogLab V7"""
    
    # CAMINHOS DE ARQUIVOS
    FONT_BASE_PATH = 'lib/fonts'
    ASSETS_PATH = 'assets'
    AUDIO_PATH = 'assets/audio'
    MUSIC_PATH = 'assets/audio/music'
    SFX_PATH = 'assets/audio/sfx'
    GAME_AUDIO_PATH = 'assets/audio/game'
    UI_AUDIO_PATH = 'assets/audio/ui'
    
    # CONFIGURAÇÕES DE ÁUDIO
    DEFAULT_BEEP_DURATION = 0.2
    DEFAULT_BEEP_FREQUENCY = 1000
    DEFAULT_BUZZER_VOLUME = 5000  # duty_u16 value
    
    # Frequências de notas musicais (em Hz)
    MUSICAL_NOTES = {
        'C4': 261.63, 'CS4': 277.18, 'D4': 293.66, 'DS4': 311.13,
        'E4': 329.63, 'F4': 349.23, 'FS4': 369.99, 'G4': 392.00,
        'GS4': 415.30, 'A4': 440.00, 'AS4': 466.16, 'B4': 493.88,
        'C5': 523.25, 'CS5': 554.37, 'D5': 587.33, 'DS5': 622.25,
        'E5': 659.25, 'F5': 698.46, 'FS5': 739.99, 'G5': 783.99,
        'GS5': 830.61, 'A5': 880.00, 'AS5': 932.33, 'B5': 987.77
    }
    
    # CORES PADRÃO (RGB para NeoPixel)
    COLORS = {
        'RED': (50, 0, 0),
        'GREEN': (0, 50, 0),
        'BLUE': (0, 0, 50),
        'YELLOW': (30, 30, 0),
        'MAGENTA': (30, 0, 30),
        'CYAN': (0, 30, 30),
        'WHITE': (25, 25, 25),
        'BLACK': (0, 0, 0),
        'ORANGE': (50, 25, 0),
        'PURPLE': (25, 0, 50),
        'PINK': (50, 20, 30),
        # Cores brilhantes
        'BRIGHT_RED': (255, 0, 0),
        'BRIGHT_GREEN': (0, 255, 0),
        'BRIGHT_BLUE': (0, 0, 255),
        'BRIGHT_WHITE': (255, 255, 255),
        'BRIGHT_YELLOW': (255, 255, 0),
        'BRIGHT_CYAN': (0, 255, 255),
        'BRIGHT_MAGENTA': (255, 0, 255)
    }
    
    # CONFIGURAÇÕES DE DEBUG E LOGGING
    DEBUG_MODE = True
    VERBOSE_LOGGING = False
    PERFORMANCE_MONITORING = False
    ERROR_RECOVERY = True
    
    # CONFIGURAÇÕES DE JOGOS E APLICAÇÕES
    GAME_FPS = 30
    MENU_SCROLL_SPEED = 0.2
    ANIMATION_STEPS = 10
    
    # CONFIGURAÇÕES DE REDE (Para Pico W)
    WIFI_TIMEOUT = 10
    DEFAULT_HOSTNAME = 'bitdoglab'
    
    # VALIDAÇÃO E SEGURANÇA
    VALIDATE_PIN_CONFLICTS = True
    SAFE_MODE_ON_ERROR = True
    AUTO_RECOVERY = True

# =============================================================================
# ALIASES PARA ACESSO DIRETO
# =============================================================================

# Instâncias para acesso direto
PINS = PinConfig
HARDWARE = HardwareConfig
SOFTWARE = SoftwareConfig

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_pin_config():
    """Retorna configuração de pinos"""
    return PINS

def get_hardware_config():
    """Retorna configuração de hardware"""
    return HARDWARE

def get_software_config():
    """Retorna configuração de software"""
    return SOFTWARE
