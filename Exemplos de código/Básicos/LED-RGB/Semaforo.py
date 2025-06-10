from machine import Pin
from utime import sleep

# LEDs RGB da BitDogLab
led_vermelho = Pin(13, Pin.OUT)  # R
led_verde = Pin(11, Pin.OUT)     # G
led_azul = Pin(12, Pin.OUT)      # B (não usado nesse exemplo)

while True:
    # 🟢 Verde — siga
    led_vermelho.value(0)
    led_verde.value(1)
    sleep(3)
    
    # 🟡 Amarelo — atenção (usando vermelho + verde juntos)
    for i in range(3):
        led_vermelho.value(1)
        led_verde.value(1)
        sleep(0.5)
        led_vermelho.value(0)
        led_verde.value(0)
        sleep(0.5)

    # 🔴 Vermelho — pare
    led_vermelho.value(1)
    led_verde.value(0)
    sleep(4)

    # Apaga todos antes de recomeçar
    led_vermelho.value(0)
    led_verde.value(0)
    sleep(0.5)


