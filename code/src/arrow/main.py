
from utime import sleep
import neopixel
import random
import time

from config import NUM_LEDS, PIN, oled, joystick_x, joystick_y, np

''' Este código é de um jogo onde aleatóriamente é impressa uma seta,
    para cima, para baixo, para esquerda ou para a direita.
    Ele recebe o input do usuário pelo joystick, se acertar, a matriz fica verde,
     se errar, vermelha
'''

def display_message(message):
    """Mostra uma mensagem no display OLED."""
    oled.fill(0)
    oled.text(message, 0, 25)
    oled.show()
def apagar():
    np.fill((0, 0, 0))
    np.write()

def desenhar_seta(direcao):
    """
    Desenha uma seta na matriz com base na direção:
    'cima', 'baixo', 'esquerda', 'direita'
    """
    apagar()
    if direcao == "cima":
        coords = [2, 7, 12, 17, 22, 6, 8, 10, 14]  # Seta para cima
    elif direcao == "baixo":
        coords = [2, 7, 12, 17, 22, 10, 14, 16, 18]  # Seta para baixo
    elif direcao == "esquerda":
        coords = [10, 11, 12, 13, 14, 2, 6, 16, 22]  # Seta para a esquerda
    elif direcao == "direita":
        coords = [10, 11, 12, 13, 14, 2, 8, 18, 22]  # Seta para a direita
    else:
        return

    for c in coords:
        np[c] = (0, 0, 50)  # Cor azul para a seta
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
    """
    Dá feedback na matriz de LEDs:
    - Verde se a direção estiver correta
    - Vermelho se a direção estiver errada
    """
    apagar()
    if correto:
        cor = (0, 50, 0)  # Verde
        coords = [1, 2, 3, 5, 10, 15, 21, 22, 23, 19, 14, 9] # Círculo
        for c in coords:
            np[c] = cor
        np.write()
        sleep(0.5)
        return
    cor = (50, 0, 0)  # Vermelho
    coords = [0, 6, 12, 18, 24, 4, 8, 16, 20] # Xis
    for c in coords:
        np[c] = cor
    np.write()
    sleep(0.5)
    

print("Jogo iniciado! Movimente o joystick para a direção da seta.")

while True:
    # Inicializa variáveis do jogo
    vidas = 5
    score = 0
    time = 1.0  # Tempo inicial para a seta desaparecer

    while vidas > 0:  # O jogo continua enquanto o jogador tiver vidas
        # Escolhe uma direção aleatória
        direcao_esperada = random.choice(["cima", "baixo", "esquerda", "direita"])
        desenhar_seta(direcao_esperada)

        # Aguarda o jogador fazer um movimento
        acertou = False
        while not acertou:
            direcao_jogador = ler_joystick()
            if direcao_jogador != "centro":  # Evita reagir enquanto o joystick está no centro
                acertou = direcao_jogador == direcao_esperada
                
                if acertou:
                    score += 1  # Incrementa o placar
                    feedback(True)
                    display_message(f"Score: {score}")
                    
                    # Aumenta a dificuldade (diminui o tempo) a cada 5 acertos
                    if not (score % 5):
                        time = max(0.5, time - 0.1)  # Reduz o tempo, mínimo de 0.5 segundos
                else:
                    vidas -= 1  # Reduz as vidas em caso de erro
                    feedback(False)
                    display_message(f"Vidas: {vidas}/5")
                
                break  # Sai do loop para gerar a próxima seta

        sleep(time)  # Pausa antes de mostrar a próxima seta

    # Exibe mensagem de fim de jogo
    apagar()
    display_message("Fim de Jogo!")
    print(f"Score final: {score}")
    sleep(2)

    # Reinicia o jogo
    apagar()
    display_message("Novo jogo em 3s...")
    sleep(3)

