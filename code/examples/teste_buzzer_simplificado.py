# Exemplo de uso do sistema de buzzer simplificado
from lib.buzzer import play_audio, set_global_volume, get_global_volume, Buzzer
import time

# Configurações
BUZZER_PIN = 21
AUDIO_PATH = "assets/audio"

def teste_sistema_buzzer():
    """Testa o sistema de buzzer simplificado"""
    
    print("=== Teste do Sistema de Buzzer Simplificado ===")
    
    # 1. Teste de nota individual usando a classe
    print("1. Testando nota individual...")
    buzzer = Buzzer(BUZZER_PIN, default_volume=0.3)
    buzzer.play_note(440, duration=0.5)  # Lá 440Hz por 0.5s
    time.sleep(0.5)
    
    # 2. Teste da função global com uma música
    print("2. Testando música - Nokia...")
    try:
        play_audio(BUZZER_PIN, f"{AUDIO_PATH}/music/nokia.txt", volume=0.3)
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao tocar Nokia: {e}")
    
    # 3. Teste de volume global
    print("3. Testando controle de volume global...")
    print(f"Volume atual: {get_global_volume()}")
    set_global_volume(0.5)
    
    try:
        play_audio(BUZZER_PIN, f"{AUDIO_PATH}/music/happybirthday.txt", volume=0.3)
        time.sleep(1)
    except Exception as e:
        print(f"Erro ao tocar Happy Birthday: {e}")
    
    # 4. Teste de som de jogo
    print("4. Testando sons de jogo...")
    game_sounds = ["coin_collect", "power_up", "victory"]
    for sound in game_sounds:
        try:
            print(f"Tocando: {sound}")
            play_audio(BUZZER_PIN, f"{AUDIO_PATH}/game/{sound}.txt", volume=0.4)
            time.sleep(0.5)
        except Exception as e:
            print(f"Erro ao tocar {sound}: {e}")
    
    # 5. Teste de fade
    print("5. Testando fade in/out...")
    buzzer.play_note_with_fade(523, duration=3.0, fade_in_time=0.5, fade_out_time=0.5)
    time.sleep(0.5)
    
    # 6. Teste de loop (apenas alguns segundos)
    print("6. Testando loop (3 segundos)...")
    try:
        import _thread
        import time
        
        # Inicia o loop em uma thread separada
        def play_loop():
            play_audio(BUZZER_PIN, f"{AUDIO_PATH}/music/nokia.txt", volume=0.2, loop=True)
        
        # Simula loop por alguns segundos (em produção, você cancelaria com KeyboardInterrupt)
        print("Iniciando loop... (simulação)")
        buzzer.play_note(262, 0.1)  # Dó rápido
        buzzer.play_note(294, 0.1)  # Ré rápido
        buzzer.play_note(330, 0.1)  # Mi rápido
        print("Loop simulado concluído")
        
    except Exception as e:
        print(f"Erro no teste de loop: {e}")
    
    print("7. Silenciando sistema...")
    buzzer.stop()
    
    print("Teste concluído! ✅")

def demo_musicas():
    """Demonstração de várias músicas disponíveis"""
    print("\n=== Demo de Músicas ===")
    
    musicas = [
        "nokia.txt",
        "happybirthday.txt", 
        "supermariobros.txt",
        "zeldaslullaby.txt",
        "tetris.txt"
    ]
    
    for musica in musicas:
        print(f"Tocando: {musica}")
        try:
            play_audio(BUZZER_PIN, f"{AUDIO_PATH}/music/{musica}", volume=0.3)
            time.sleep(1)  # Pausa entre músicas
        except Exception as e:
            print(f"Erro ao tocar {musica}: {e}")

if __name__ == "__main__":
    # Executa os testes
    teste_sistema_buzzer()
    
    # Pergunta se quer ouvir as músicas
    resposta = input("\nDeseja ouvir demonstração de músicas? (s/n): ").lower()
    if resposta == 's':
        demo_musicas()
