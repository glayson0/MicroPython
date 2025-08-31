from machine import PWM, Pin
import neopixel
import time
import random
from machine import Pin, ADC
from ssd1306 import SSD1306_I2C
import math

# Número de LEDs na sua matriz 5x5
NUM_LEDS = 25

# Definindo a matriz de LEDs
LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

np = neopixel.NeoPixel(Pin(7), NUM_LEDS)

def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# apagar todos os LEDs
def clear_all():
    for i in range(len(np)):
        np[i] = (0,0,0)
    np.write()

# Inicialização do Neopixel e ADC para o microfone
#np = neopixel.NeoPixel(machine.Pin(PIN_NUM), NUM_LEDS)
adc = machine.ADC(machine.Pin(28))  # GP28 para o microfone

OFFSET = int(1.65 / 3.3 * 65536)  # Valor ADC correspondente a 1,65V

# Definição dos patamares
patamares = [
    [2],
    [1, 2, 3],
    [7, 1, 2, 3],
    [12, 6, 7, 8, 0, 1, 2, 3, 4],
    [12, 6, 7, 8, 0, 1, 2, 3, 4, 11, 13, 17, 5, 9],
    [12, 6, 7, 8, 0, 1, 2, 3, 4, 11, 13, 17, 5, 9, 22, 16, 18, 10, 14],
    [12, 6, 7, 8, 0, 1, 2, 3, 4, 11, 13, 17, 5, 9, 22, 16, 18, 10, 14, 15, 19],
    [12, 6, 7, 8, 0, 1, 2, 3, 4, 11, 13, 17, 5, 9, 22, 16, 18, 10, 14, 15, 19, 20, 21, 23, 24]
] * 2

def determinar_cor(patamar_index):
    if patamar_index < len(patamares) / 3.5:
        return (0, 0, 85)  # Azul
    else:
        return (105, 0, 0)  # Vermelho

def acender_leds(patamar_index):
    cor = determinar_cor(patamar_index)
    
    # Primeiro, desligamos todos os LEDs
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)

    # Depois, acendemos os LEDs do patamar atual
    for i in patamares[patamar_index]:
        np[i] = cor
        
    np.write()

def acender_por_valor(ratio):
    max_patamares = len(patamares)
    patamar_index = int(ratio * max_patamares)
    patamar_index = min(patamar_index, max_patamares - 1)  # Evitar índices fora da faixa

    # Se o ratio estiver abaixo de um limiar, desliga todos os LEDs
    if ratio < 0.05:
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)
        np.write()
    else:
        acender_leds(patamar_index)


def vu_meter(adc_value):
    volume = max(0, (adc_value - OFFSET)*2)  # Subtrai o offset e garante que o valor seja positivo
    volume_ratio = volume / 65536.0
    normalized_ratio = math.pow(volume_ratio, 0.5)  # Ajustando a sensibilidade

    acender_por_valor(normalized_ratio)

clear_all()

while True:
    adc_value = adc.read_u16()  # Lendo o valor do ADC do microfone
    vu_meter(adc_value)  # Atualizando o VU meter com base no valor do ADC
    time.sleep(0.02)  # Um pequeno atraso para tornar o loop manejável
       
