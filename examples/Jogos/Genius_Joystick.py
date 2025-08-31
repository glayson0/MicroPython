from machine import Pin, ADC, SoftI2C, PWM
from ssd1306 import SSD1306_I2C
from utime import sleep
import neopixel
import random

# ----- Configuração da matriz de LEDs -----
NUM_LEDS = 25
PIN = 7
np = neopixel.NeoPixel(Pin(PIN), NUM_LEDS)

# ----- Configuração do display OLED -----
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c_oled)

# ----- Configuração do buzzer (opcional) -----
buzzer = PWM(Pin(21))
def tocar_nota(freq, duracao=0.2):
    buzzer.freq(freq)
    buzzer.duty_u16(1000)
    sleep(duracao)
    buzzer.duty_u16(0)

# ----- Configuração do joystick -----
joystick_x = ADC(27)
joystick_y = ADC(26)

# ----- Mapas e parâmetros -----
direcoes = ["cima", "baixo", "esquerda", "direita"]
notas = {"cima": 330, "baixo": 349, "esquerda": 262, "direita": 294}
setas = {
    "cima": [2, 7, 12, 17, 22, 6, 8, 10, 14],
    "baixo": [2, 7, 12, 17, 22, 10, 14, 16, 18],
    "esquerda": [10, 11, 12, 13, 14, 2, 6, 16, 22],
    "direita": [10, 11, 12, 13, 14, 2, 8, 18, 22]
}

# ----- Funções auxiliares -----
def apagar():
    np.fill((0, 0, 0))
    np.write()

def display_message(msg):
    oled.fill(0)
    oled.text(msg, 0, 25)
    oled.show()

def desenhar_seta(direcao, cor=(0, 0, 50)):
    apagar()
    for c in setas[direcao]:
        np[c] = cor
    np.write()

def ler_joystick():
    x = joystick_x.read_u16()
    y = joystick_y.read_u16()
    if x < 15000:
        return "esquerda"
    elif x > 50000:
        return "direita"
    elif y < 15000:
        return "cima"
    elif y > 50000:
        return "baixo"
    else:
        return "centro"

def feedback(correto):
    apagar()
    if correto:
        cor = (0, 50, 0)  # Verde
        coords = [1,2,3,5,10,15,21,22,23,19,14,9]
    else:
        cor = (50, 0, 0)  # Vermelho
        coords = [0, 6, 12, 18, 24, 4, 8, 16, 20]
    for c in coords:
        np[c] = cor
    np.write()
    sleep(0.5)
    apagar()

# ----- Lógica do GENIUS -----
def mostrar_sequencia(seq):
    for direcao in seq:
        desenhar_seta(direcao)
        tocar_nota(notas[direcao])
        sleep(0.5)
        apagar()
        sleep(0.2)

def jogar_genius():
    nivel = 1
    sequencia = []

    display_message("GENIUS Joystick")
    sleep(2)

    while True:
        display_message(f"Nivel {nivel}")
        sleep(1)

        sequencia.append(random.choice(direcoes))
        mostrar_sequencia(sequencia)

        display_message("Sua vez!")
        sleep(0.5)

        for esperado in sequencia:
            while True:
                entrada = ler_joystick()
                if entrada != "centro":
                    break
                sleep(0.05)

            desenhar_seta(entrada, (50, 50, 0))
            tocar_nota(notas[entrada])
            sleep(0.3)

            if entrada != esperado:
                display_message("Errou!")
                feedback(False)
                sleep(2)
                display_message("Score: " + str(nivel - 1))
                sleep(3)
                return

            feedback(True)

        nivel += 1
        sleep(1)

# ----- Início do jogo -----
while True:
    jogar_genius()
    display_message("Novo jogo em 3s")
    sleep(3)

