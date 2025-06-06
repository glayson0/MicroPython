'''
Pressionar alternadamente o botão A e B liga e desliga o LED central.
'''

from machine import Pin
import utime

# Configuração dos pinos
botao_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Configura o botão A com pull-up interno
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)  # Configura o botão B com pull-up interno
led_vermelho = Pin(13, Pin.OUT) 

while True:
    # Lê o estado dos botões
    estado_a = botao_a.value()
    estado_b = botao_b.value()

    if estado_a == 0:
        led_vermelho.value(1)
    elif estado_b == 0:
        led_vermelho.value(0)

    utime.sleep(0.1)  # Delay para evitar leituras muito rápidas