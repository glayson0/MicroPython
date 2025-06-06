'''
Toca notas, onde joystick para esquerda é Dó, para a direita é Ré, para cima Mi, para baixo Fá
Já os botões B é Sol e 
'''

from machine import Pin, PWM, ADC
import utime

# Configuração dos GPIOs
buzzer = PWM(Pin(21))  # Buzzer A
button_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão A
button_b = Pin(6, Pin.IN, Pin.PULL_UP)  # Botão B
joystick_x = ADC(Pin(27))  # Eixo X do joystick
joystick_y = ADC(Pin(26))  # Eixo Y do joystick

# Notas musicais (frequências em Hz)
NOTAS = {
    "do": 262,  
    "re": 294,  
    "mi": 330,  
    "fa": 349,  
    "sol": 392,
    "la": 440,
    "si": 494  
}

def tocar_nota(frequencia, duracao=0.2):
    """Toca uma nota no buzzer."""
    if frequencia > 0:  # Frequência válida
        buzzer.freq(frequencia)
        buzzer.duty_u16(1000)  # Volume médio
        utime.sleep(duracao)
        buzzer.duty_u16(0)  # Para o som

# Loop principal
print("Use o joystick e o botão B para tocar as notas musicais.")

while True:
    # Leitura do joystick
    posicao_x = joystick_x.read_u16()
    posicao_y = joystick_y.read_u16()
    
    # Identifica a direção do joystick
    if posicao_x < 20000:  # Joystick para esquerda
        print("Tocando Dó")
        tocar_nota(NOTAS["do"])
    elif posicao_x > 45000:  # Joystick para direita
        print("Tocando Ré")
        tocar_nota(NOTAS["re"])
    elif posicao_y < 20000:  # Joystick para baixo
        print("Tocando Fá")
        tocar_nota(NOTAS["fa"])
    elif posicao_y > 45000:  # Joystick para cima
        print("Tocando Mi")
        tocar_nota(NOTAS["mi"])
    # Verifica se o botão B foi pressionado
    if button_b.value() == 0:  # Botão B pressionado
        print("Tocando Sol")
        tocar_nota(NOTAS["sol"])
    if button_a.value() == 0:
        print("Tocando Lá")
        tocar_nota(NOTAS["la"])
    if button_a.value() == 0 and button_b() == 0:
        print("Tocando Si")
        tocar_nota(NOTAS["si"])
    
    
    utime.sleep(0.1)  # Pausa para evitar leituras consecutivas


