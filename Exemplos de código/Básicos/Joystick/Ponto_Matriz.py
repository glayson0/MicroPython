from machine import PWM, Pin, ADC
import neopixel
import utime

# Número de LEDs
NUM_LEDS = 25
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

# Mapeamento da matriz 5x5
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Inicializar ADC para VRx (X) e VRy (Y)
adc_vrx = ADC(Pin(27))
adc_vry = ADC(Pin(26))

# Botão do joystick
joystick_button = Pin(22, Pin.IN, Pin.PULL_UP)

# Cores possíveis
cores = [
    (0, 0, 50),    # Azul
    (0, 50, 0),    # Verde
    (50, 0, 0),    # Vermelho
    (50, 50, 0),   # Amarelo
    (50, 0, 50),   # Roxo
    (0, 50, 50),   # Ciano
    (30, 30, 30)   # Branco
]
indice_cor = 0

# Beep com buzzer no GPIO21 (opcional)
def star_trek_beep():
    buzzer = PWM(Pin(21))
    buzzer.freq(1500)
    buzzer.duty_u16(30000)
    utime.sleep(0.1)
    buzzer.duty_u16(0)
    buzzer.deinit()

# Posição inicial (centro da matriz)
x = 2
y = 2

# Zona morta do joystick (valor ADC de 16 bits)
zona_morta = 5000  # ~5% em torno do centro

# Loop principal
while True:
    vrx = adc_vrx.read_u16()
    vry = adc_vry.read_u16()

    # Centro ideal do joystick: ~32768
    centro = 32768

    # Verifica se o valor saiu da zona morta e atualiza posição
    if vrx < centro - zona_morta:
        x = max(0, x - 1)
    elif vrx > centro + zona_morta:
        x = min(4, x + 1)

    if vry < centro - zona_morta:
        y = min(4, y + 1)  # Y invertido: baixo no joystick = aumentar linha
    elif vry > centro + zona_morta:
        y = max(0, y - 1)

    # Limpa matriz
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)

    # Acende o ponto na posição atual
    np[LED_MATRIX[y][x]] = cores[indice_cor]
    np.write()

    # Verifica botão do joystick
    if not joystick_button.value():
        indice_cor = (indice_cor + 1) % len(cores)
        star_trek_beep()

    utime.sleep(0.15)

