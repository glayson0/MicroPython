"""
Classe Buzzer Genérica para MicroPython
Suporta qualquer buzzer passivo conectado via PWM
Compatível com reprodução de notas, melodias e efeitos sonoros
"""

from machine import PWM, Pin
import time

AUDIO_PATH = "assets/audio/"

# =============================================================================
# CONSTANTES DE NOTAS MUSICAIS (FREQUÊNCIAS EM HZ)
# =============================================================================

# Oitava 0
NOTE_B0 = 31

# Oitava 1
NOTE_C1 = 33
NOTE_CS1 = 35
NOTE_D1 = 37
NOTE_DS1 = 39
NOTE_E1 = 41
NOTE_F1 = 44
NOTE_FS1 = 46
NOTE_G1 = 49
NOTE_GS1 = 52
NOTE_A1 = 55
NOTE_AS1 = 58
NOTE_B1 = 62

# Oitava 2
NOTE_C2 = 65
NOTE_CS2 = 69
NOTE_D2 = 73
NOTE_DS2 = 78
NOTE_E2 = 82
NOTE_F2 = 87
NOTE_FS2 = 93
NOTE_G2 = 98
NOTE_GS2 = 104
NOTE_A2 = 110
NOTE_AS2 = 117
NOTE_B2 = 123

# Oitava 3
NOTE_C3 = 131
NOTE_CS3 = 139
NOTE_D3 = 147
NOTE_DS3 = 156
NOTE_E3 = 165
NOTE_F3 = 175
NOTE_FS3 = 185
NOTE_G3 = 196
NOTE_GS3 = 208
NOTE_A3 = 220
NOTE_AS3 = 233
NOTE_B3 = 247

# Oitava 4 (Mais comum)
NOTE_C4 = 262
NOTE_CS4 = 277
NOTE_D4 = 294
NOTE_DS4 = 311
NOTE_E4 = 330
NOTE_F4 = 349
NOTE_FS4 = 370
NOTE_G4 = 392
NOTE_GS4 = 415
NOTE_A4 = 440  # Lá padrão (440Hz)
NOTE_AS4 = 466
NOTE_B4 = 494

# Oitava 5
NOTE_C5 = 523
NOTE_CS5 = 554
NOTE_D5 = 587
NOTE_DS5 = 622
NOTE_E5 = 659
NOTE_F5 = 698
NOTE_FS5 = 740
NOTE_G5 = 784
NOTE_GS5 = 831
NOTE_A5 = 880
NOTE_AS5 = 932
NOTE_B5 = 988

# Oitava 6
NOTE_C6 = 1047
NOTE_CS6 = 1109
NOTE_D6 = 1175
NOTE_DS6 = 1245
NOTE_E6 = 1319
NOTE_F6 = 1397
NOTE_FS6 = 1480
NOTE_G6 = 1568
NOTE_GS6 = 1661
NOTE_A6 = 1760
NOTE_AS6 = 1865
NOTE_B6 = 1976

# Oitava 7
NOTE_C7 = 2093
NOTE_CS7 = 2217
NOTE_D7 = 2349
NOTE_DS7 = 2489
NOTE_E7 = 2637
NOTE_F7 = 2794
NOTE_FS7 = 2960
NOTE_G7 = 3136
NOTE_GS7 = 3322
NOTE_A7 = 3520
NOTE_AS7 = 3729
NOTE_B7 = 3951

# Oitava 8
NOTE_C8 = 4186
NOTE_CS8 = 4435
NOTE_D8 = 4699
NOTE_DS8 = 4978

# Silêncio
REST = 0

# =============================================================================
# VOLUME GLOBAL DO SISTEMA
# =============================================================================

# Volume global do sistema (0.0 a 1.0)
GLOBAL_VOLUME = 0.5

class Buzzer:
    """
    Classe genérica para controle de buzzer passivo via PWM
    
    Parâmetros:
    - pin: GPIO do buzzer (obrigatório)
    - default_volume: Volume padrão (0.0 a 1.0)
    - pwm_frequency: Frequência base do PWM (padrão: 1000Hz)
    """
    
    def __init__(self, pin, default_volume=0.3, pwm_frequency=1000):
        """
        Inicializa buzzer genérico
        
        Args:
            pin: Número do pino GPIO do buzzer
            default_volume: Volume padrão (0.0 a 1.0)
            pwm_frequency: Frequência PWM base
        """
        self.pin_number = pin
        self._buzzer = PWM(Pin(pin))
        self._default_volume = max(0.0, min(1.0, default_volume))
        self._pwm_frequency = pwm_frequency
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
        freq_int = int(freq)
        self._buzzer.freq(freq_int)
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
            
            import re
            
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
                    
                    # Obtém a frequência da nota (usando globals do próprio módulo)
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
                    
        except Exception as e:
            print(f"Erro ao carregar arquivo de áudio: {e}")
    
    # === Métodos Utilitários ===
    
    def get_info(self):
        """Retorna informações de configuração do buzzer"""
        return {
            "pin": self.pin_number,
            "volume": self._default_volume,
            "pwm_frequency": self._pwm_frequency,
            "is_playing": self._is_playing,
        }
    
    def __str__(self):
        """Representação em string do buzzer"""
        return f"Buzzer(GPIO{self.pin_number}, Volume={self._default_volume:.1f})"


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


# === Exemplo de Uso ===
if __name__ == "__main__":
    # Mini demo simples do buzzer usando config.py
    print("Mini Demo Buzzer - Notas e Beeps (usando config.py)")
    
    try:
        # Importa configurações do BitDogLab V7
        from config import PINS
        
        # Cria buzzer usando configurações do config.py
        buzzer = Buzzer(pin=PINS.BUZZER, default_volume=0.3)
        
        print(f"Buzzer criado: {buzzer}")
        print("Testando sons basicos...")
        
        # Teste 1: Beep simples
        print("1. Beep simples (1000Hz)")
        buzzer.play_note(1000, 0.3)
        time.sleep(0.5)
        
        # Teste 2: Escala musical
        print("2. Escala musical Do-Re-Mi")
        # Usa as constantes NOTE_* integradas
        notas = [NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4, NOTE_C5]
        for freq in notas:
            buzzer.play_note(freq, 0.2)
            time.sleep(0.1)
        
        # Teste 3: Melodia simples com constantes
        print("3. Melodia 'Parabéns' (simplificada)")
        parabens = [
            (NOTE_C4, 0.3), (NOTE_C4, 0.2), (NOTE_D4, 0.5),
            (NOTE_C4, 0.5), (NOTE_F4, 0.5), (NOTE_E4, 1.0)
        ]
        for freq, duration in parabens:
            buzzer.play_note(freq, duration)
            time.sleep(0.1)
        
        # Teste 4: Música da pasta
        print("4. Música da pasta (ex: asabranca.txt)")
        play_audio(PINS.BUZZER, AUDIO_PATH + "music/asabranca.txt", volume=0.3)

        print("Demo finalizada com sucesso!")
        
    except ImportError as e:
        print(f"Modulo nao encontrado ({e}) - usando valores fixos:")
        # Fallback para valores hardcoded se config.py não existir
        buzzer = Buzzer(pin=21, default_volume=0.3)  # GPIO21 = Buzzer BitDogLab
        print("Buzzer: GPIO21 (fallback)")
        print("Beep de teste...")
        buzzer.play_note(1000, 0.5)
        print("Teste concluido!")
        
    except Exception as e:
        print(f"Erro: {e}")