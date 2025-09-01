from lib.events import *
from lib.scene import Scene
from lib.config import SOFTWARE
from lib.leds import LEDMatrix
import os
import time


class MediaPlayer(Scene):
    """Media Player para reproduzir músicas em modo lista"""
    
    def __init__(self, name="Media Player", parent=None):
        super().__init__(name, parent)
        
        # Hardware específico do media player
        self.ledmatrix = None
        
        # Estado do player
        self.music_dir = SOFTWARE.MUSIC_PATH + "/"
        self.files = []
        self.selected_index = 0
        
        # Estado de reprodução
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.song_position = 0
        self.total_notes = 0
        self.current_notes = []
        
        # Timing para reprodução
        self.last_playback_update = 0
        self.playback_interval = 100
    
    def init_hardware(self):
        """Inicializa hardware do media player"""
        super().init_hardware()  # Inicializa hardware base
        
        print("🔧 Inicializando Media Player...")
        
        # LED Matrix
        try:
            self.ledmatrix = LEDMatrix()
            print("✅ LED Matrix inicializada")
        except Exception as e:
            print(f"⚠️  LED Matrix não disponível: {e}")
            self.ledmatrix = None
        
        # Carrega músicas disponíveis
        self.load_music_directory()
        
        # Inicializa LED com pattern pause
        self.update_led_status()
        
        # Inicializa timer de reprodução
        self.last_playback_update = time.ticks_ms()
        
        print(f"🎵 Media Player pronto! {len(self.files)} músicas disponíveis")
    
    def update_led_status(self):
        """Atualiza padrão LED baseado no status de reprodução"""
        if not self.ledmatrix:
            return
            
        try:
            if self.is_playing and not self.is_paused:
                # Música tocando - pattern play
                self.ledmatrix.set_pattern('play')
                self.ledmatrix.draw()
            elif self.is_paused or not self.is_playing:
                # Música pausada/parada - pattern pause  
                self.ledmatrix.set_pattern('pause')
                self.ledmatrix.draw()
        except Exception as e:
            print(f"Erro ao atualizar LED status: {e}")
            # Em caso de erro, limpa a matriz
            self.ledmatrix.clear()
    
    def load_music_directory(self):
        """Carrega arquivos de música do diretório"""
        try:
            self.files = []
            
            # Lista arquivos .txt de música
            for file in os.listdir(self.music_dir):
                if file.endswith('.txt'):
                    self.files.append(file)
            
            # Ordena arquivos
            self.files.sort()
            
            # Reset da seleção
            self.selected_index = 0
            
            print(f"Músicas carregadas: {len(self.files)}")
            print(f"Arquivos: {self.files}")
                
        except Exception as e:
            print(f"Erro ao carregar diretório de música: {e}")
            self.files = []
    
    def get_display_name(self, filename):
        """Formata nome do arquivo para exibição"""
        name = filename.replace('.txt', '').replace('_', ' ')
        # Capitaliza primeira letra de cada palavra
        return ' '.join(word for word in name.split())
    
    def load_song(self, filename):
        """Carrega notas de uma música (suporta formatos simples e Arduino)"""
        try:
            filepath = self.music_dir + filename
            print(f"📂 Carregando música: {filepath}")
            
            # Verifica se arquivo existe
            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
            except OSError:
                print(f"❌ Arquivo não encontrado: {filepath}")
                return False
            
            if not content:
                print(f"❌ Arquivo vazio: {filepath}")
                return False
            
            # Detecta formato do arquivo
            if self._detect_arduino_format(content):
                print("📋 Formato musical (Arduino/Híbrido) detectado")
                notes = self._parse_arduino_format(content)
            else:
                print("📋 Formato simples (frequência:duração) detectado")
                notes = self._parse_simple_format(content)
            
            if not notes:
                print(f"❌ Nenhuma nota válida encontrada em {filename}")
                return False
            
            self.current_notes = notes
            self.total_notes = len(notes)
            self.song_position = 0
            
            print(f"✅ Música carregada com sucesso: {len(notes)} notas válidas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar música {filename}: {e}")
            self.current_notes = []
            self.total_notes = 0
            return False
    
    def _detect_arduino_format(self, content):
        """Detecta se o arquivo está no formato Arduino ou híbrido"""
        # Procura por padrões típicos sem usar flags avançadas do regex
        
        # Verifica se tem NOTE_XXX:Y (formato Arduino)
        has_arduino = 'NOTE_' in content and ':' in content
        
        # Verifica se tem padrões como C4:, D4:, etc. (formato híbrido)
        has_hybrid = False
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Procura por padrões C4:, D4:, etc. na linha
                parts = line.split()
                for part in parts:
                    if ':' in part:
                        note_part = part.split(':')[0]
                        # Verifica se é uma nota musical (C4, D4, etc.)
                        if len(note_part) >= 2 and note_part[0].upper() in 'ABCDEFG' and note_part[-1].isdigit():
                            has_hybrid = True
                            break
                if has_hybrid:
                    break
        
        # Verifica se tem frequências numéricas puras (formato simples)
        has_simple_freq = False
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    try:
                        # Tenta converter o primeiro parte para número
                        freq = int(parts[0].strip())
                        # Se conseguiu converter e não tem NOTE_ ou letras de nota, é formato simples
                        if not has_arduino and not has_hybrid:
                            has_simple_freq = True
                            break
                    except ValueError:
                        continue
        
        # Se tem frequências numéricas puras, é formato simples
        if has_simple_freq and not has_arduino and not has_hybrid:
            return False
        
        # Se tem NOTE_XXX ou nomes de notas, é formato Arduino/híbrido
        return has_arduino or has_hybrid
    
    def _parse_simple_format(self, content):
        """Parser para formato simples: frequência:duração por linha"""
        notes = []
        line_count = 0
        
        for line in content.split('\n'):
            line = line.strip()
            line_count += 1
            
            if line and not line.startswith('#'):
                if ':' in line:
                    try:
                        note_part, duration_part = line.split(':', 1)
                        frequency = int(note_part.strip())
                        duration = float(duration_part.strip())
                        notes.append((frequency, duration))
                        print(f"  📝 Linha {line_count}: {frequency}Hz por {duration}s")
                    except ValueError as e:
                        print(f"  ⚠️  Linha {line_count} ignorada (erro de formato): {line}")
                        continue
        
        return notes
    
    def _parse_arduino_format(self, content):
        """Parser para formato Arduino: NOTE_XXX:Y com múltiplas notas por linha"""
        
        # Extrai tempo/BPM do cabeçalho (busca manual)
        tempo = 120  # Valor padrão
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#') and 'Tempo:' in line and 'BPM' in line:
                # Extrai número do tempo manualmente
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'Tempo:' and i + 1 < len(parts):
                            tempo = int(parts[i + 1])
                            break
                except (ValueError, IndexError):
                    pass
                break
        
        print(f"  🎵 Tempo: {tempo} BPM")
        
        # Mapeamento de notas para frequências
        note_frequencies = self._get_note_frequency_map()
        
        # Remove comentários e processa notas
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        
        # Junta todas as linhas e separa por espaços
        melody_text = ' '.join(lines)
        notes_data = melody_text.split()
        
        # Calcula duração de uma nota inteira em segundos
        wholenote_ms = (60000 * 4) // tempo  # em milissegundos
        wholenote_sec = wholenote_ms / 1000.0  # em segundos
        
        notes = []
        note_count = 0
        
        for note_str in notes_data:
            if ':' not in note_str:
                continue
                
            try:
                note_name, duration_str = note_str.split(':')
                duration_val = int(duration_str)
                
                # Obtém frequência da nota
                freq = note_frequencies.get(note_name, 0)
                
                # Calcula duração da nota
                if duration_val > 0:
                    # Nota normal
                    note_duration_sec = wholenote_sec / duration_val
                elif duration_val < 0:
                    # Nota pontuada (duração negativa)
                    note_duration_sec = wholenote_sec / abs(duration_val)
                    note_duration_sec *= 1.5  # Aumenta em 50%
                else:
                    continue  # Ignora duração zero
                
                notes.append((freq, note_duration_sec))
                note_count += 1
                
                note_name_display = note_name if note_name != 'REST' else 'SILÊNCIO'
                print(f"  🎵 Nota {note_count}: {note_name_display} ({freq}Hz) por {note_duration_sec:.3f}s")
                
            except ValueError as e:
                print(f"  ⚠️  Nota ignorada (erro de formato): {note_str}")
                continue
        
        return notes
    
    def _get_note_frequency_map(self):
        """Retorna mapeamento de nomes de notas para frequências"""
        return {
            'REST': 0,
            # Formato híbrido (C4, D4, etc.)
            'C3': 131, 'CS3': 139, 'D3': 147, 'DS3': 156,
            'E3': 165, 'F3': 175, 'FS3': 185, 'G3': 196,
            'GS3': 208, 'A3': 220, 'AS3': 233, 'B3': 247,
            'C4': 262, 'CS4': 277, 'D4': 294, 'DS4': 311,
            'E4': 330, 'F4': 349, 'FS4': 370, 'G4': 392,
            'GS4': 415, 'A4': 440, 'AS4': 466, 'B4': 494,
            'C5': 523, 'CS5': 554, 'D5': 587, 'DS5': 622,
            'E5': 659, 'F5': 698, 'FS5': 740, 'G5': 784,
            'GS5': 831, 'A5': 880, 'AS5': 932, 'B5': 988,
            'C6': 1047, 'CS6': 1109, 'D6': 1175, 'DS6': 1245,
            'E6': 1319, 'F6': 1397, 'FS6': 1480, 'G6': 1568,
            'GS6': 1661, 'A6': 1760, 'AS6': 1865, 'B6': 1976,
            # Formato Arduino (NOTE_XXX)
            'NOTE_C3': 131, 'NOTE_CS3': 139, 'NOTE_D3': 147, 'NOTE_DS3': 156,
            'NOTE_E3': 165, 'NOTE_F3': 175, 'NOTE_FS3': 185, 'NOTE_G3': 196,
            'NOTE_GS3': 208, 'NOTE_A3': 220, 'NOTE_AS3': 233, 'NOTE_B3': 247,
            'NOTE_C4': 262, 'NOTE_CS4': 277, 'NOTE_D4': 294, 'NOTE_DS4': 311,
            'NOTE_E4': 330, 'NOTE_F4': 349, 'NOTE_FS4': 370, 'NOTE_G4': 392,
            'NOTE_GS4': 415, 'NOTE_A4': 440, 'NOTE_AS4': 466, 'NOTE_B4': 494,
            'NOTE_C5': 523, 'NOTE_CS5': 554, 'NOTE_D5': 587, 'NOTE_DS5': 622,
            'NOTE_E5': 659, 'NOTE_F5': 698, 'NOTE_FS5': 740, 'NOTE_G5': 784,
            'NOTE_GS5': 831, 'NOTE_A5': 880, 'NOTE_AS5': 932, 'NOTE_B5': 988,
            'NOTE_C6': 1047, 'NOTE_CS6': 1109, 'NOTE_D6': 1175, 'NOTE_DS6': 1245,
            'NOTE_E6': 1319, 'NOTE_F6': 1397, 'NOTE_FS6': 1480, 'NOTE_G6': 1568,
            'NOTE_GS6': 1661, 'NOTE_A6': 1760, 'NOTE_AS6': 1865, 'NOTE_B6': 1976,
        }
    
    def play_song(self):
        """Inicia reprodução da música selecionada"""
        if not self.files or self.selected_index >= len(self.files):
            print("Nenhuma música selecionada!")
            return False
        
        selected_file = self.files[self.selected_index]
        print(f"Tentando tocar: {selected_file}")
        
        if self.load_song(selected_file):
            self.current_song = selected_file
            self.is_playing = True
            self.is_paused = False
            self.song_position = 0
            self.last_playback_update = time.ticks_ms()  # Reset timer
            self.update_led_status()  # Atualiza LED para pattern play
            print(f"✅ Reprodução iniciada: {selected_file} ({len(self.current_notes)} notas)")
            
            # Som de confirmação
            if self.buzzer:
                self.buzzer.play_note(1000, 0.1)
            
            return True
        else:
            print(f"❌ Erro ao carregar música: {selected_file}")
            return False
    
    def pause_resume(self):
        """Pausa ou retoma a reprodução"""
        if self.is_playing:
            self.is_paused = not self.is_paused
            status = "pausada" if self.is_paused else "retomada"
            print(f"Música {status}")
            
            # Atualiza LED status
            self.update_led_status()
            
            # Som de feedback
            if self.buzzer:
                feedback_freq = 600 if self.is_paused else 800
                self.buzzer.play_note(feedback_freq, 0.05)
    
    def stop_song(self):
        """Para a reprodução"""
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.song_position = 0
        self.update_led_status()  # Atualiza LED para pattern pause
        print("Reprodução parada")
    
    def update_playback(self):
        """Atualiza reprodução da música (sistema não-bloqueante)"""
        if not self.is_playing or self.is_paused or not self.current_notes:
            return
        
        # Verifica se há nota para tocar
        if self.song_position < len(self.current_notes):
            frequency, duration = self.current_notes[self.song_position]
            
            print(f"🎵 Tocando nota {self.song_position + 1}/{len(self.current_notes)}: {frequency}Hz por {duration}s")
            
            # Toca nota de forma não-bloqueante
            if self.buzzer and frequency > 0:
                # Para reprodução não-bloqueante, usa duração reduzida
                note_duration = min(duration, 0.2)  # Máximo 200ms por nota
                self.buzzer.play_note(frequency, note_duration)
            elif frequency == 0:
                # Silêncio - apenas espera
                print("🔇 Silêncio...")
            
            # Avança posição
            self.song_position += 1
            
            # Atualiza timing para próxima nota
            # Usa a duração original da nota para timing correto
            next_note_delay = int(duration * 1000)  # Converte para ms
            self.playback_interval = max(50, min(next_note_delay, 500))  # Entre 50ms e 500ms
            
            # Verifica se música terminou
            if self.song_position >= len(self.current_notes):
                print("🎵 Música finalizada!")
                self.stop_song()
        else:
            # Não há mais notas para tocar
            self.stop_song()
    
    def get_playback_status(self):
        """Retorna status da reprodução para exibição"""
        if not self.is_playing:
            return "Parado"
        elif self.is_paused:
            return "Pausado"
        else:
            progress = 0
            if self.total_notes > 0:
                progress = int((self.song_position / self.total_notes) * 100)
            return f"Tocando {progress}%"
    
    def render(self):
        """Renderiza interface do media player usando layout padrão"""
        # Formata arquivos para exibição  
        display_items = []
        for filename in self.files:
            display_items.append(self.get_display_name(filename))
        
        # Prepara título com status
        status = self.get_playback_status()
        title = f"= PLAYER ({status}) ="
        
        # Usa renderização padrão
        self.render_standard_layout(
            title=title,
            items=display_items,
            selected_index=self.selected_index,
            footer="= A:OK  B:Back ="
        )
    
    def handle_events(self):
        """Processa eventos do media player"""
        import time
        
        # Polling obrigatório dos eventos
        if self.events:
            from lib.events import poll
            poll()
        
        # Processa eventos próprios se ainda rodando
        if not self.running:
            return
            
        # Usa as funções globais do sistema de eventos
        from lib.events import get, JOYSTICK_UP, JOYSTICK_DOWN, BUTTON_A_DOWN, BUTTON_B_DOWN
        
        for event in get():
            if event == JOYSTICK_UP:
                self.navigate_up()
                self.needs_render = True  # Marca para re-renderizar
                
            elif event == JOYSTICK_DOWN:
                self.navigate_down()
                self.needs_render = True  # Marca para re-renderizar
                
            elif event == BUTTON_A_DOWN:
                # Botão A: Play música selecionada
                print(f"🎮 Botão A pressionado - tentando tocar música...")
                success = self.play_song()
                if success:
                    print(f"✅ Comando de reprodução enviado com sucesso!")
                else:
                    print(f"❌ Falha ao iniciar reprodução")
                    # Som de erro se falhar
                    if self.buzzer:
                        self.buzzer.play_note(400, 0.2)
                self.needs_render = True  # Marca para re-renderizar
                
            elif event == BUTTON_B_DOWN:
                # Botão B: Pausar/Retomar se música tocando, senão volta
                if self.is_playing:
                    # Se música estiver tocando, pausa/retoma
                    print(f"🎮 Botão B pressionado - pausando/retomando música...")
                    self.pause_resume()
                    self.needs_render = True  # Marca para re-renderizar
                else:
                    # Se não estiver tocando, volta para menu pai
                    print(f"🎮 Botão B pressionado - voltando ao menu...")
                    self.goto_parent()
        
        # Verifica botão B diretamente também (para compatibilidade com classe base)
        if self.button_b and self.button_b.is_pressed():
            if not self.is_playing:
                # Só volta se não estiver tocando música
                self.goto_parent()
                time.sleep(0.2)  # Debounce
    
    def update(self):
        """Atualiza reprodução da música"""
        if not self.is_playing or self.is_paused or not self.current_notes:
            return
        
        current_time = time.ticks_ms()
        time_elapsed = time.ticks_diff(current_time, self.last_playback_update)
        
        # Verifica se é hora de tocar a próxima nota
        if time_elapsed >= self.playback_interval:
            self.update_playback()
            self.last_playback_update = current_time
            
            # Re-renderiza se estiver tocando para mostrar progresso
            if self.is_playing:
                self.needs_render = True
    
    def navigate_up(self):
        """Navega para cima na lista"""
        if self.files and self.selected_index > 0:
            self.selected_index -= 1
            
            # Som de navegação
            if self.buzzer:
                self.buzzer.play_note(800, 0.03)
    
    def navigate_down(self):
        """Navega para baixo na lista"""
        if self.files and self.selected_index < len(self.files) - 1:
            self.selected_index += 1
            
            # Som de navegação
            if self.buzzer:
                self.buzzer.play_note(800, 0.03)
    
    def cleanup(self):
        """Limpa recursos do media player"""
        if self.ledmatrix:
            self.ledmatrix.clear()
        super().cleanup()


def media_player():
    """Função para executar o media player"""
    app = MediaPlayer()
    app.run()


# Execução direta
if __name__ == "__main__":
    media_player()
