from machine import PWM, Pin
import time
# Importa apenas as constantes necessárias para o formato Zelda
from music_notes import *

# Pino padrão do buzzer
BUZZER_PIN = 21

# Volume global do sistema (0.0 a 1.0)
GLOBAL_VOLUME = 0.5

class Buzzer:
    def __init__(self, pin, default_volume=0.3):
        self._buzzer = PWM(Pin(pin))
        self._default_volume = default_volume
        self._max_duty = 65535
        self._is_playing = False
        self._current_volume = 0.0
        self._fade_steps = 20
        
        # Caminho base para os arquivos de áudio
        self.audio_path = "/home/gnbo/bitdoglab/MicroPython/assets/audio"
        
    def set_volume(self, volume):
        """Define o volume (0.0 a 1.0)"""
        self._default_volume = max(0.0, min(1.0, volume))
    
    def _get_effective_volume(self, volume=None):
        """Calcula o volume efetivo considerando volume global"""
        local_volume = volume or self._default_volume
        return local_volume * GLOBAL_VOLUME
    
    def _set_pwm_volume(self, volume):
        """Define o volume direto no PWM"""
        self._current_volume = volume
        duty = int(self._max_duty * volume)
        self._buzzer.duty_u16(duty)
    
    def play_note(self, freq, duration=0.2, volume=None):
        """Toca uma nota"""
        effective_volume = self._get_effective_volume(volume)
        
        # Garante que a frequência seja um inteiro
        self._buzzer.freq(int(freq))
        self._set_pwm_volume(effective_volume)
        self._is_playing = True
        time.sleep(duration)
        self._set_pwm_volume(0)
        self._is_playing = False
    
    def fade_in(self, freq, volume=None, duration=1.0):
        """Fade in de um tom"""
        target_volume = self._get_effective_volume(volume)
        # Garante que a frequência seja um inteiro
        self._buzzer.freq(int(freq))
        self._is_playing = True
        
        step_duration = duration / self._fade_steps
        volume_step = target_volume / self._fade_steps
        
        for i in range(self._fade_steps + 1):
            current_vol = volume_step * i
            self._set_pwm_volume(current_vol)
            time.sleep(step_duration)
    
    def fade_out(self, duration=1.0):
        """Fade out do som atual"""
        if not self._is_playing:
            return
            
        start_volume = self._current_volume
        step_duration = duration / self._fade_steps
        volume_step = start_volume / self._fade_steps
        
        for i in range(self._fade_steps + 1):
            current_vol = start_volume - (volume_step * i)
            self._set_pwm_volume(max(0, current_vol))
            time.sleep(step_duration)
        
        self._is_playing = False
    
    def play_note_with_fade(self, freq, duration=2.0, volume=None, fade_in_time=0.3, fade_out_time=0.3):
        """Toca uma nota com fade in e fade out"""
        if duration <= (fade_in_time + fade_out_time):
            # Se a duração for muito curta, toca sem fade
            self.play_note(freq, duration, volume)
            return
        
        # Fade in
        self.fade_in(freq, volume, fade_in_time)
        
        # Sustenta o som
        sustain_time = duration - fade_in_time - fade_out_time
        time.sleep(sustain_time)
        
        # Fade out
        self.fade_out(fade_out_time)
    
    def play_audio_file(self, file_path, volume=None):
        """Toca um arquivo de áudio (formato FREQ:DURATION:VOLUME ou NOTA:DURATION)"""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Remove comentários e linhas vazias
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    lines.append(line)
            
            # Processa cada linha
            for line in lines:
                parts = line.split(':')
                if len(parts) < 2:
                    continue
                
                freq_or_note = parts[0]
                duration_ms = int(parts[1])
                file_volume = float(parts[2]) if len(parts) > 2 else None
                
                # Converte nota para frequência se necessário
                if freq_or_note.isdigit() or freq_or_note == "0":
                    freq = int(freq_or_note)
                else:
                    # Tenta buscar pela constante global (formato NOTE_*)
                    freq = globals().get(f"NOTE_{freq_or_note}", 0)
                    if freq == 0 and freq_or_note == "REST":
                        freq = REST
                
                # Usa volume do arquivo ou padrão
                use_volume = file_volume if file_volume is not None else volume
                
                # Toca a nota
                if freq > 0:
                    self.play_note(freq, duration_ms / 1000.0, use_volume)
                else:
                    time.sleep(duration_ms / 1000.0)  # Silêncio
                    
        except Exception as e:
            print(f"Erro ao carregar arquivo de áudio: {e}")
    
    def stop(self):
        """Para o som imediatamente"""
        self._set_pwm_volume(0)
        self._is_playing = False

# Instância global do buzzer
buzzer = Buzzer(BUZZER_PIN)

# Funções globais
def set_global_volume(volume):
    """Define o volume global do sistema"""
    global GLOBAL_VOLUME
    GLOBAL_VOLUME = max(0.0, min(1.0, volume))

def get_global_volume():
    """Retorna o volume global atual"""
    return GLOBAL_VOLUME

def mute_all():
    """Silencia o sistema"""
    set_global_volume(0.0)
    buzzer.stop()

# Teste
if __name__ == "__main__":    
    print("=== Teste Buzzer com Sistema de Arquivos ===")
    
    print("1. Nota simples")
    buzzer.play_note(440, 0.3)
    time.sleep(0.5)
    
    print("2. Som de UI - Click")
    buzzer.play_audio_file(f"{buzzer.audio_path}/ui/click.txt")
    time.sleep(0.3)
    
    print("3. Som de jogo - Coin collect")
    buzzer.play_audio_file(f"{buzzer.audio_path}/game/coin_collect.txt")
    time.sleep(0.5)
    
    print("4. Efeito sonoro - R2D2")
    buzzer.play_audio_file(f"{buzzer.audio_path}/sfx/r2d2.txt")
    time.sleep(1)
    
    print("5. Testando volume global")
    print(f"Volume global atual: {get_global_volume()}")
    set_global_volume(0.3)
    print(f"Volume global alterado para: {get_global_volume()}")
    buzzer.play_audio_file(f"{buzzer.audio_path}/ui/success.txt")
    time.sleep(0.5)
    
    print("6. Música - Escala")
    try:
        buzzer.play_audio_file(f"{buzzer.audio_path}/music/escala.txt")
    except Exception as e:
        print(f"Erro ao tocar música: {e}")
    
    print("7. Diversos sons de jogo:")
    game_sounds = ["pause", "resume", "power_up", "victory"]
    for sound in game_sounds:
        print(f"Tocando: {sound}")
        buzzer.play_audio_file(f"{buzzer.audio_path}/game/{sound}.txt")
        time.sleep(0.3)
    
    print("8. Testando fade in/out:")
    print("Nota com fade in e fade out")
    buzzer.play_note_with_fade(440, duration=3.0, fade_in_time=0.5, fade_out_time=0.5)
    time.sleep(0.5)
    
    print("Fade in manual + fade out")
    buzzer.fade_in(880, duration=1.0)
    time.sleep(1.0)
    buzzer.fade_out(duration=1.0)
    
    print("Teste concluído!")