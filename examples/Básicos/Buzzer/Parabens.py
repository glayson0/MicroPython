from machine import Pin, PWM
from utime import sleep

# Configuração do buzzer
BUZZER_PIN = 21  # GPIO conectado ao buzzer
buzzer = PWM(Pin(BUZZER_PIN))

# Frequências das notas musicais em Hertz
NOTES = {
    "C": 261,   # Dó
    "D": 294,   # Ré
    "E": 329,   # Mi
    "F": 349,   # Fá
    "G": 392,   # Sol
    "A": 440,   # Lá
    "B": 493    # Si
}

# Função para tocar uma nota
def tocar_nota(nota, duracao):
    if nota in NOTES:
        buzzer.freq(NOTES[nota])   # Define a frequência da nota
        buzzer.duty_u16(2000)      # Define o volume (ajustável)
        sleep(duracao)             # Toca a nota pelo tempo definido
        buzzer.duty_u16(0)         # Para o som
        sleep(0.1)                 # Pausa curta entre as notas

# Melodia completa de "Parabéns pra Você"
melodia_parabens = [
    ("C", 0.3), ("C", 0.3), ("D", 0.5), ("C", 0.5), ("F", 0.5), ("E", 0.7),
    ("C", 0.3), ("C", 0.3), ("D", 0.5), ("C", 0.5), ("G", 0.5), ("F", 0.7),
    ("C", 0.3), ("C", 0.3), ("A", 0.5), ("F", 0.5), ("E", 0.5), ("D", 0.8),
    ("B", 0.3), ("B", 0.3), ("A", 0.5), ("F", 0.5), ("G", 0.5), ("F", 0.7), 
]

# Função para tocar uma melodia genérica
def tocar_melodia(melodia):
    for nota, duracao in melodia:
        tocar_nota(nota, duracao)

# Programa principal
print("Tocando a melodia completa de 'Parabéns pra Você'")
tocar_melodia(melodia_parabens)

