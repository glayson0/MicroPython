from machine import PWM, Pin
import time
import re
# Importa apenas as constantes necessárias para o formato Zelda
from music_notes import *

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
    
    def stop(self):
        """Para o som imediatamente"""
        self._set_pwm_volume(0)
        self._is_playing = False

    def play_audio_file(self, file_path, volume=None):
        """Toca um arquivo de áudio (formato Arduino/Zelda)"""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            self._play_arduino_format(content, volume)
                    
        except Exception as e:
            print(f"Erro ao carregar arquivo de áudio: {e}")
    
    def _play_arduino_format(self, content, volume):
        """Toca formato Arduino (NOTE_X:duration com BPM)"""
        # Extrai o tempo do arquivo
        tempo_match = re.search(r'# Tempo: (\d+) BPM', content)
        tempo = int(tempo_match.group(1)) if tempo_match else 120
        
        # Remove comentários e linhas vazias
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        
        # Junta todas as linhas e separa por espaços
        melody_text = ' '.join(lines)
        notes_data = melody_text.split()
        
        # Calcula duração de uma nota inteira em milissegundos
        wholenote = (60000 * 4) // tempo
        
        for note_str in notes_data:
            if ':' not in note_str:
                continue
                
            try:
                note_name, duration_str = note_str.split(':')
                duration_val = int(duration_str)
                
                # Obtém a frequência da nota
                freq = globals().get(note_name, 0)
                
                # Calcula duração da nota
                if duration_val > 0:
                    # Nota normal
                    note_duration = wholenote // duration_val
                else:
                    # Nota pontuada (duração negativa)
                    note_duration = wholenote // abs(duration_val)
                    note_duration = int(note_duration * 1.5)  # Aumenta em 50%
                
                # Converte para segundos
                duration_sec = note_duration / 1000.0
                
                # Toca a nota (90% da duração, 10% pausa)
                play_duration = duration_sec * 0.9
                pause_duration = duration_sec * 0.1
                
                if freq > 0:
                    self.play_note(freq, play_duration, volume)
                else:
                    time.sleep(play_duration)  # Silêncio
                
                time.sleep(pause_duration)  # Pausa entre notas
                
            except ValueError as e:
                print(f"Erro ao processar nota '{note_str}': {e}")
                continue

# Função global genérica para tocar qualquer arquivo de áudio
def play_audio(pin, file_path, volume=0.3, loop=False):
    """
    Função global para tocar qualquer arquivo de áudio no buzzer.
    
    Args:
        pin (int): Número do pino do buzzer
        file_path (str): Caminho para o arquivo de áudio (.txt)
        volume (float): Volume de 0.0 a 1.0 (padrão: 0.3)
        loop (bool): Se True, toca em loop contínuo (padrão: False)
    
    Formato do arquivo .txt:
        # Comentários começam com #
        # Tempo: 120 BPM (opcional, padrão é 120)
        NOTE_C4:4 NOTE_D4:4 NOTE_E4:2 REST:4
        NOTE_F4:8 NOTE_G4:8 NOTE_A4:1
        
    Onde:
        - NOTE_XXX: Nota musical (ex: NOTE_C4, NOTE_A4, etc.)
        - REST: Silêncio
        - :X: Duração da nota (1=semibreve, 2=mínima, 4=semínima, 8=colcheia, etc.)
        - Duração negativa (-4) = nota pontuada (50% mais longa)
    """
    buzzer = Buzzer(pin, volume)
    
    try:
        while True:
            buzzer.play_audio_file(file_path, volume)
            if not loop:
                break
    except KeyboardInterrupt:
        print("Reprodução interrompida pelo usuário")
    finally:
        buzzer.stop()

# Funções globais para controle de volume
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