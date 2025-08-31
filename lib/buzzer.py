from machine import PWM, Pin
import time

# Pino padrão do buzzer
BUZZER_PIN = 21

# Volume global do sistema (0.0 a 1.0)
GLOBAL_VOLUME = 0.01

class Buzzer:
    def __init__(self, pin, default_volume=0.3):
        self._buzzer = PWM(Pin(pin))
        self._default_volume = default_volume
        self._max_duty = 65535
        self._is_playing = False
        self._current_volume = 0.0
        self._fade_steps = 20
        
        # Sons predefinidos
        self.sounds = {
            "click": (1200, 0.05, 0.3),
            "hover": (800, 0.03, 0.2),
            "error": (300, 0.3, 0.4),
            "success": [(800, 0.1), (1000, 0.1), (1200, 0.2)],
            "blip": (1000, 0.02, 0.3),

            "pause": [(600, 0.2, 0.4), (0, 0.1), (400, 0.3, 0.3)],
            "resume": [(400, 0.2, 0.3), (0, 0.1), (600, 0.2, 0.4)],
            "coin_collect": [(523, 0.1), (659, 0.1), (784, 0.15)],
            "power_up": [(220, 0.08), (277, 0.08), (330, 0.08), (440, 0.08)],
            "power_down": [(440, 0.08), (330, 0.08), (277, 0.08), (220, 0.08)],
            "level_complete": [(523, 0.2), (659, 0.2), (784, 0.2), (1047, 0.4)],
            "game_over": [(440, 0.2), (415, 0.2), (392, 0.2), (370, 0.3)],
            "victory": [(523, 0.2), (659, 0.2), (784, 0.2), (1047, 0.8)],
            "health_low": [(200, 0.1, 0.6), (0, 0.05), (180, 0.1, 0.6)],
            "countdown_tick": (800, 0.1, 0.5),
            "countdown_final": (1200, 0.5, 0.7), 
            
            "r2d2": [(4000, 0.1), (0, 0.05), (5000, 0.15), (0, 0.05), (4500, 0.12)],
            "star_trek": [(1000, 0.1), (0, 0.05), (1500, 0.1), (0, 0.05), (2000, 0.1)],
            
            "song1": [(440, 0.5), (660, 0.5), (880, 0.5)],
            "song2": [(523, 0.5), (659, 0.5), (784, 0.5)],
            "song3": [(587, 0.5), (739, 0.5), (880, 0.5)]
        }
        
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
        
        self._buzzer.freq(int(freq))
        self._set_pwm_volume(effective_volume)
        self._is_playing = True
        time.sleep(duration)
        self._set_pwm_volume(0)
        self._is_playing = False

    def play_sound(self, notes, volume=None, fade_in=None, fade_out=None, loop=False):
        """
        Toca uma lista de notas
        notes: [(freq, duration), ...] ou [freq, ...] ou tupla simples (freq, duration, volume)
        """
        if not notes:
            return
        
        # Se for tupla simples (freq, duration, volume), toca diretamente
        if isinstance(notes, tuple) and len(notes) >= 2 and isinstance(notes[0], (int, float)):
            freq, duration = notes[0], notes[1]
            note_volume = notes[2] if len(notes) > 2 else volume
            self.play_note(freq, duration, note_volume)
            return
        
        while True:
            # Fade in
            if fade_in and fade_in > 0:
                first_freq = self._get_first_freq(notes)
                if first_freq:
                    self.fade_in(first_freq, volume, fade_in)
            
            # Toca as notas
            for note in notes:
                if isinstance(note, tuple) and len(note) >= 2:
                    freq, duration = note[0], note[1]
                    note_volume = note[2] if len(note) > 2 else volume
                    if freq > 0:
                        self.play_note(freq, duration, note_volume)
                    else:
                        time.sleep(duration)  # silêncio
                elif isinstance(note, (int, float)):
                    if note > 0:
                        self.play_note(note, 0.2, volume)
                    else:
                        time.sleep(0.2)  # silêncio
            
            # Fade out
            if fade_out and fade_out > 0:
                last_freq = self._get_last_freq(notes)
                if last_freq:
                    self._buzzer.freq(int(last_freq))
                    self._set_pwm_volume(self._get_effective_volume(volume))
                    self._is_playing = True
                    self.fade_out(fade_out)
            
            if not loop:
                break
            time.sleep(0.1)  # pausa entre loops
    
    def fade_in(self, freq, volume=None, duration=1.0):
        """Fade in de um tom"""
        target_volume = self._get_effective_volume(volume)
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
    
    def mute(self):
        """Para o som imediatamente"""
        self._set_pwm_volume(0)
        self._is_playing = False
    
    def _get_first_freq(self, notes):
        """Obtém a primeira frequência válida"""
        if not notes:
            return None
        first = notes[0]
        if isinstance(first, tuple):
            return first[0] if first[0] > 0 else None
        elif isinstance(first, (int, float)):
            return first if first > 0 else None
        return None
    
    def _get_last_freq(self, notes):
        """Obtém a última frequência válida"""
        if not notes:
            return None
        last = notes[-1]
        if isinstance(last, tuple):
            return last[0] if last[0] > 0 else None
        elif isinstance(last, (int, float)):
            return last if last > 0 else None
        return None
    
    def list_sounds(self):
        """Lista todos os sons disponíveis"""
        print("Sons disponíveis:", list(self.sounds.keys()))

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
    buzzer.mute()

# Teste
if __name__ == "__main__":    
    print("=== Teste Buzzer Básico ===")
    
    print("1. Nota simples")
    buzzer.play_note(440, 0.3)
    time.sleep(0.5)
    
    print("2. Som do dicionário")
    buzzer.play_sound(buzzer.sounds["click"])
    time.sleep(0.3)
    
    print("3. Sequência com fade")
    notes = [(440, 0.2), (554, 0.2), (659, 0.3)]
    buzzer.play_sound(notes, fade_in=0.2, fade_out=0.2)
    time.sleep(1)
    
    print("4. Som com loop (3x)")
    short_melody = [(523, 0.1), (659, 0.1)]
    for _ in range(3):
        buzzer.play_sound(short_melody)
        time.sleep(0.1)
    
    print("5. Frequências simples com pausa")
    simple_freqs = [440, 0, 554, 0, 659]  # 0 = silêncio
    buzzer.play_sound(simple_freqs, volume=0.5)
    time.sleep(1)
    
    print("6. Sons do dicionário")
    buzzer.list_sounds()
    buzzer.play_sound(buzzer.sounds["success"])
    time.sleep(0.5)
    buzzer.play_sound(buzzer.sounds["coin_collect"])
    
    print("Teste concluído!")