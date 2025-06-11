from machine import Pin
import neopixel
from utime import sleep
import ssd1306 

# Configurações da matriz de LEDs
NUM_LEDS = 25  # Total de LEDs na matriz 5x5
PIN = 7  # Pino onde a matriz Neopixel está conectada
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

# Mapeamento da matriz de LEDs com a origem no canto superior esquerdo
LED_MATRIX = [
    [0, 1, 2, 3, 4],
    [5, 6, 7, 8, 9],
    [10, 11, 12, 13, 14],
    [15, 16, 17, 18, 19],
    [20, 21, 22, 23, 24]
]

# Configuração dos botões
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão A (com pull-up interno)
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)  # Botão B (com pull-up interno)

# Variável para controlar o índice atual na matriz
led_index = 0

# Função para apagar todos os LEDs 
def apagar():
    np.fill((0, 0, 0))  # Todos os LEDs desligados
    np.write()

# Função para acender o próximo LED e exibir na tela OLED
def acender_proximo(cor, cor_nome):
    global led_index
    if led_index < NUM_LEDS:
        np[led_index] = cor  # Define a cor do LED atual
        np.write()
        led_index += 1  # Avança para o próximo LED
    else:
        led_index = 0  # Reseta a contagem
        apagar()  # Apaga todos os LEDs

# Programa principal
print("Pressione Botão A para vermelho, Botão B para azul.")

while True:
    if not botao_a.value():  # Botão A pressionado
        acender_proximo((50, 0, 0), "Vermelho")  # LED vermelho
        sleep(0.2)  # Debounce para evitar múltiplos cliques rápidos

    if not botao_b.value():  # Botão B pressionado
        acender_proximo((0, 0, 50), "Azul")  # LED azul
        sleep(0.2) 

