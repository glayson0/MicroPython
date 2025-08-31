import time

class Scene:
    """Classe base para todas as cenas do jogo"""
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.paused = False
        
    def enter(self):
        """Chamado quando a cena é iniciada"""
        self.active = True
        self.paused = False
        
    def update(self, dt):
        """Chamado a cada frame para atualizar a lógica - dt = delta time em segundos"""
        pass
        
    def draw(self):
        """Chamado a cada frame para desenhar"""
        pass
        
    def handle_input(self, input_event):
        """Processa eventos de input (botões, joystick)"""
        pass
        
    def exit(self):
        """Chamado quando a cena é encerrada"""
        self.active = False
        
    def pause(self):
        """Pausa a cena"""
        self.paused = True
        
    def resume(self):
        """Resume a cena"""
        self.paused = False

class InputEvent:
    """Classe para representar eventos de entrada"""
    def __init__(self, source, action, data=None):
        self.source = source      # 'button_a', 'button_b', 'joystick'
        self.action = action      # 'press', 'release', 'long_press', 'move', 'direction_change'
        self.data = data          # dados específicos do evento
        self.timestamp = time.ticks_ms()

class Timer:
    """Sistema de timer para a game engine"""
    def __init__(self):
        self.timers = {}
        
    def create_timer(self, name, duration, callback, repeat=False):
        """Cria um timer
        Args:
            name: nome único do timer
            duration: duração em segundos
            callback: função a ser chamada quando o timer expira
            repeat: se deve repetir automaticamente
        """
        self.timers[name] = {
            'duration': duration,
            'remaining': duration,
            'callback': callback,
            'repeat': repeat,
            'active': True
        }
    
    def update(self, dt):
        """Atualiza todos os timers"""
        expired_timers = []
        
        for name, timer in self.timers.items():
            if not timer['active']:
                continue
                
            timer['remaining'] -= dt
            
            if timer['remaining'] <= 0:
                # Timer expirou
                if timer['callback']:
                    timer['callback']()
                
                if timer['repeat']:
                    timer['remaining'] = timer['duration']
                else:
                    expired_timers.append(name)
        
        # Remove timers que expiraram e não repetem
        for name in expired_timers:
            del self.timers[name]
    
    def stop_timer(self, name):
        """Para um timer"""
        if name in self.timers:
            self.timers[name]['active'] = False
    
    def remove_timer(self, name):
        """Remove um timer"""
        if name in self.timers:
            del self.timers[name]

class GameState:
    """Sistema para gerenciar estado global do jogo"""
    def __init__(self):
        self.data = {}
        
    def set(self, key, value):
        """Define um valor no estado"""
        self.data[key] = value
        
    def get(self, key, default=None):
        """Obtém um valor do estado"""
        return self.data.get(key, default)
    
    def increment(self, key, amount=1):
        """Incrementa um valor numérico"""
        current = self.get(key, 0)
        self.set(key, current + amount)
        
    def reset(self):
        """Reseta todo o estado"""
        self.data.clear()

class SceneManager:
    """Gerenciador de cenas"""
    def __init__(self):
        self.scenes = {}
        self.scene_stack = []
        self.current_scene = None
        
    def register_scene(self, name, scene_class):
        """Registra uma classe de cena"""
        self.scenes[name] = scene_class
        
    def push_scene(self, name, *args, **kwargs):
        """Empilha uma nova cena (mantém a anterior)"""
        if self.current_scene:
            self.current_scene.pause()
            self.scene_stack.append(self.current_scene)
            
        scene_class = self.scenes[name]
        self.current_scene = scene_class(*args, **kwargs)
        self.current_scene.enter()
        
    def pop_scene(self):
        """Remove a cena atual e volta para a anterior"""
        if self.current_scene:
            self.current_scene.exit()
            
        if self.scene_stack:
            self.current_scene = self.scene_stack.pop()
            self.current_scene.resume()
        else:
            self.current_scene = None
            
    def change_scene(self, name, *args, **kwargs):
        """Troca completamente de cena"""
        if self.current_scene:
            self.current_scene.exit()
            
        self.scene_stack.clear()
        scene_class = self.scenes[name]
        self.current_scene = scene_class(*args, **kwargs)
        self.current_scene.enter()
        
    def get_current_scene(self):
        """Retorna a cena atual"""
        return self.current_scene

class GameEngine:
    """Engine principal do jogo"""
    def __init__(self, matrix, oled, joystick, button_a, button_b, buzzer):
        # Módulos dos periféricos
        self.matrix = matrix
        self.oled = oled
        self.joystick = joystick
        self.button_a = button_a
        self.button_b = button_b
        self.buzzer = buzzer
        
        # Sistemas da engine
        self.scene_manager = SceneManager()
        self.timer_system = Timer()
        self.game_state = GameState()
        
        # Controle de tempo
        self.last_time = time.ticks_ms()
        self.target_fps = 30
        self.frame_time = 1000 // self.target_fps  # em ms
        
        # Estado da engine
        self.running = False
        self.debug_mode = False
        
        # Input tracking
        self.last_joystick_direction = "center"
        
        # Configura callbacks dos botões
        self._setup_input_callbacks()
        
    def _setup_input_callbacks(self):
        """Configura os callbacks de entrada"""
        self.button_a.on_press(lambda: self._handle_input('button_a', 'press'))
        self.button_a.on_release(lambda: self._handle_input('button_a', 'release'))
        self.button_a.on_long_press(lambda: self._handle_input('button_a', 'long_press'))
        
        self.button_b.on_press(lambda: self._handle_input('button_b', 'press'))
        self.button_b.on_release(lambda: self._handle_input('button_b', 'release'))
        self.button_b.on_long_press(lambda: self._handle_input('button_b', 'long_press'))
        
        self.joystick.on_press(lambda: self._handle_input('joystick', 'press'))
        
    def _handle_input(self, source, action, data=None):
        """Processa eventos de entrada"""
        event = InputEvent(source, action, data)
        
        current_scene = self.scene_manager.get_current_scene()
        if current_scene and current_scene.active and not current_scene.paused:
            current_scene.handle_input(event)
    
    def _update_joystick(self):
        """Verifica mudanças no joystick"""
        current_direction = self.joystick.get_direction()
        
        if current_direction != self.last_joystick_direction:
            self._handle_input('joystick', 'direction_change', {
                'direction': current_direction,
                'previous': self.last_joystick_direction,
                'normalized': self.joystick.get_normalized()
            })
            self.last_joystick_direction = current_direction
            
        # Sempre envia eventos de movimento se não estiver no centro
        if current_direction != "center":
            self._handle_input('joystick', 'move', {
                'direction': current_direction,
                'normalized': self.joystick.get_normalized()
            })
    
    def register_scene(self, name, scene_class):
        """Registra uma cena na engine"""
        self.scene_manager.register_scene(name, scene_class)
        
    def start_scene(self, scene_name):
        """Inicia uma cena específica"""
        self.scene_manager.change_scene(scene_name, self)
        
    def create_timer(self, name, duration, callback, repeat=False):
        """Cria um timer da engine"""
        self.timer_system.create_timer(name, duration, callback, repeat)
        
    def play_sound(self, sound_data, **kwargs):
        """Toca um som através da engine"""
        self.buzzer.play_sound(sound_data, **kwargs)
        
    def set_fps(self, fps):
        """Define o FPS alvo"""
        self.target_fps = fps
        self.frame_time = 1000 // fps
        
    def run(self):
        """Loop principal da engine"""
        self.running = True
        print("Game Engine iniciada!")
        
        try:
            while self.running:
                current_time = time.ticks_ms()
                dt = time.ticks_diff(current_time, self.last_time) / 1000.0  # delta time em segundos
                self.last_time = current_time
                
                # Atualiza sistemas
                self.timer_system.update(dt)
                
                # Processa input
                self.button_a.read()
                self.button_b.read()
                self.joystick.check_button()
                self._update_joystick()
                
                # Atualiza cena atual
                current_scene = self.scene_manager.get_current_scene()
                if current_scene and current_scene.active and not current_scene.paused:
                    current_scene.update(dt)
                    current_scene.draw()
                
                # Controla FPS
                frame_end_time = time.ticks_ms()
                frame_duration = time.ticks_diff(frame_end_time, current_time)
                
                if frame_duration < self.frame_time:
                    time.sleep_ms(self.frame_time - frame_duration)
                    
                if self.debug_mode and time.ticks_ms() % 1000 < 50:  # Debug info a cada segundo
                    print(f"FPS: {1000/(time.ticks_diff(time.ticks_ms(), current_time)):.1f}")
                    
        except KeyboardInterrupt:
            print("Game Engine encerrada pelo usuário")
        except Exception as e:
            print(f"Erro na Game Engine: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Para a engine"""
        self.running = False
        if self.scene_manager.current_scene:
            self.scene_manager.current_scene.exit()
        print("Game Engine parada")

# === Cenas de exemplo ===

class MenuScene(Scene):
    """Cena de menu principal"""
    def __init__(self, engine):
        super().__init__(engine)
        self.menu_items = ["Jogar", "Configurações", "Sobre"]
        self.selected_item = 0
        
    def enter(self):
        super().enter()
        self.engine.play_sound(self.engine.buzzer.sounds["blip"])
        self._update_display()
        
    def _update_display(self):
        """Atualiza a tela do menu"""
        lines = [{'text': "=== MENU ===", 'align': 'center'}]
        
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.selected_item else "  "
            lines.append({'text': f"{prefix}{item}", 'align': 'center'})
            
        self.engine.oled.draw_lines(lines, valign='middle')
        
        # Mostra padrão na matriz baseado no item selecionado
        patterns = ["heart", "plus", "circle"]
        if self.selected_item < len(patterns):
            self.engine.matrix.clear()
            pattern = self.engine.matrix.patterns[patterns[self.selected_item]]
            self.engine.matrix.set_pattern(pattern, (0, 255, 0), 0.1)
            self.engine.matrix.draw()
    
    def handle_input(self, event):
        if event.source == 'joystick' and event.action == 'direction_change':
            direction = event.data['direction']
            
            if direction == 'north':
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                self.engine.play_sound(self.engine.buzzer.sounds["hover"])
                self._update_display()
            elif direction == 'south':
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                self.engine.play_sound(self.engine.buzzer.sounds["hover"])
                self._update_display()
                
        elif event.source == 'button_a' and event.action == 'press':
            self._select_item()
            
    def _select_item(self):
        """Processa seleção do item do menu"""
        self.engine.play_sound(self.engine.buzzer.sounds["success"])
        
        if self.selected_item == 0:  # Jogar
            self.engine.scene_manager.change_scene('game', self.engine)
        elif self.selected_item == 1:  # Configurações
            self.engine.scene_manager.push_scene('settings', self.engine)
        elif self.selected_item == 2:  # Sobre
            self.engine.scene_manager.push_scene('about', self.engine)

class GameScene(Scene):
    """Cena principal do jogo"""
    def __init__(self, engine):
        super().__init__(engine)
        self.player_pos = [2, 2]  # posição do jogador na matriz 5x5
        self.score = 0
        self.game_time = 0
        
    def enter(self):
        super().enter()
        self.engine.play_sound(self.engine.buzzer.sounds["power_up"])
        self.engine.game_state.set('score', 0)
        self.engine.game_state.set('lives', 3)
        
        # Timer de exemplo - incrementa score a cada 2 segundos
        self.engine.create_timer('score_timer', 2.0, self._increment_score, repeat=True)
        
        self._update_display()
        
    def _increment_score(self):
        """Incrementa o score automaticamente"""
        self.engine.game_state.increment('score', 10)
        self.engine.play_sound(self.engine.buzzer.sounds["coin_collect"])
        
    def update(self, dt):
        self.game_time += dt
        if int(self.game_time) % 5 == 0 and int(self.game_time * 10) % 10 == 0:  # A cada 5 segundos
            self._update_display()
    
    def _update_display(self):
        """Atualiza display do jogo"""
        score = self.engine.game_state.get('score', 0)
        lives = self.engine.game_state.get('lives', 3)
        
        lines = [
            {'text': f"Score: {score}", 'align': 'left'},
            {'text': f"Lives: {lives}", 'align': 'left'},
            {'text': f"Time: {int(self.game_time)}s", 'align': 'left'},
            {'text': "", 'align': 'center'},
            {'text': "B = Menu", 'align': 'center'}
        ]
        self.engine.oled.draw_lines(lines)
        
        # Desenha jogador na matriz
        self.engine.matrix.clear()
        self.engine.matrix.set_led(tuple(self.player_pos), (255, 0, 0), 0.2)
        self.engine.matrix.draw()
    
    def handle_input(self, event):
        if event.source == 'joystick' and event.action == 'direction_change':
            direction = event.data['direction']
            
            # Move o jogador
            new_pos = self.player_pos.copy()
            
            if direction == 'north' and new_pos[1] > 0:
                new_pos[1] -= 1
            elif direction == 'south' and new_pos[1] < 4:
                new_pos[1] += 1
            elif direction == 'west' and new_pos[0] > 0:
                new_pos[0] -= 1
            elif direction == 'east' and new_pos[0] < 4:
                new_pos[0] += 1
                
            if new_pos != self.player_pos:
                self.player_pos = new_pos
                self.engine.play_sound(self.engine.buzzer.sounds["blip"])
                self._update_display()
                
        elif event.source == 'button_b' and event.action == 'press':
            # Volta ao menu
            self.engine.scene_manager.change_scene('menu', self.engine)
            
        elif event.source == 'button_a' and event.action == 'press':
            # Ação do jogador
            self.engine.game_state.increment('score', 50)
            self.engine.play_sound(self.engine.buzzer.sounds["coin_collect"])
            self._update_display()
    
    def exit(self):
        super().exit()
        self.engine.timer_system.remove_timer('score_timer')

class SettingsScene(Scene):
    """Cena de configurações"""
    def __init__(self, engine):
        super().__init__(engine)
        
    def enter(self):
        super().enter()
        lines = [
            {'text': "=== CONFIG ===", 'align': 'center'},
            {'text': "", 'align': 'center'},
            {'text': "Volume: Normal", 'align': 'center'},
            {'text': "FPS: 30", 'align': 'center'},
            {'text': "", 'align': 'center'},
            {'text': "B = Voltar", 'align': 'center'}
        ]
        self.engine.oled.draw_lines(lines, valign='middle')
        
        self.engine.matrix.clear()
        pattern = self.engine.matrix.patterns["plus"]
        self.engine.matrix.set_pattern(pattern, (0, 0, 255), 0.1)
        self.engine.matrix.draw()
        
    def handle_input(self, event):
        if event.source == 'button_b' and event.action == 'press':
            self.engine.scene_manager.pop_scene()

class AboutScene(Scene):
    """Cena sobre o jogo"""
    def __init__(self, engine):
        super().__init__(engine)
        
    def enter(self):
        super().enter()
        lines = [
            {'text': "BitDogLab", 'align': 'center'},
            {'text': "Mini Game", 'align': 'center'},
            {'text': "Engine", 'align': 'center'},
            {'text': "", 'align': 'center'},
            {'text': "v1.0", 'align': 'center'},
            {'text': "B = Voltar", 'align': 'center'}
        ]
        self.engine.oled.draw_lines(lines, valign='middle')
        
        self.engine.matrix.clear()
        pattern = self.engine.matrix.patterns["heart"]
        self.engine.matrix.set_pattern(pattern, (255, 0, 255), 0.1)
        self.engine.matrix.draw()
        
    def handle_input(self, event):
        if event.source == 'button_b' and event.action == 'press':
            self.engine.scene_manager.pop_scene()

# === Exemplo de uso ===
if __name__ == "__main__":
    # Importações necessárias (exemplo)
    # from matrix import LEDMatrix
    # from oled import OledScreen
    # from joystick import Joystick
    # from button import Button
    # from buzzer import buzzer
    
    print("=== Game Engine Example ===")
    print("Para usar a engine:")
    print("1. Importe os módulos de hardware")
    print("2. Crie a instância da GameEngine")
    print("3. Registre suas cenas")
    print("4. Inicie a engine")
    print()
    
    # Exemplo de inicialização:
    # matrix = LEDMatrix(7, 25)
    # oled = OledScreen()
    # joystick = Joystick(27, 26, 22)
    # button_a = Button(5)
    # button_b = Button(6)
    # 
    # engine = GameEngine(matrix, oled, joystick, button_a, button_b, buzzer)
    # 
    # engine.register_scene('menu', MenuScene)
    # engine.register_scene('game', GameScene)
    # engine.register_scene('settings', SettingsScene)
    # engine.register_scene('about', AboutScene)
    # 
    # engine.start_scene('menu')
    # engine.run()