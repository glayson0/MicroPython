# Acendimento progressivo dos LEDs na matriz na cor vermelha
from machine import Pin
import neopixel
from utime import sleep

NUM_LEDS = 25
PIN = 7
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

COR_LED = (50, 0, 0)
led_index = 0

def apagar():
    np.fill((0, 0, 0))
    np.write()

while True:
    if led_index < NUM_LEDS:
        np[led_index] = COR_LED
        np.write()
        led_index += 1
        sleep(0.1)
    else:
        apagar()
        led_index = 0
        sleep(0.2)

