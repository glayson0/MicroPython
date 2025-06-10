# Pisca LED central vermelho

from machine import Pin
from utime import sleep

led_1 = Pin(13, Pin.OUT)

while True:
    led_1.value(1) 
    sleep(1)
    led_1.value(0)  # Apaga o LED
    sleep(1)

