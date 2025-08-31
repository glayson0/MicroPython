"""
Sistema de Eventos BitDogLab V7 - Inspirado no Pygame/Godot
Permite controle manual do loop de eventos e input polling
"""

from micropython import const
try:
    from utime import ticks_ms, ticks_diff
except ImportError:
    from time import ticks_ms, ticks_diff

# =============================================================================
# CONSTANTES DE EVENTOS - Como Pygame
# =============================================================================

# Eventos de Joystick
JOYSTICK_UP = const(1)
JOYSTICK_DOWN = const(2)
JOYSTICK_LEFT = const(3)
JOYSTICK_RIGHT = const(4)
JOYSTICK_CENTER = const(5)
JOYSTICK_BUTTON_DOWN = const(6)
JOYSTICK_BUTTON_UP = const(7)

# Eventos de Botões
BUTTON_A_DOWN = const(10)
BUTTON_A_UP = const(11)
BUTTON_B_DOWN = const(12)
BUTTON_B_UP = const(13)

# Eventos de Sistema
QUIT = const(99)

class Event:
    """Classe para representar um evento - Como Pygame"""
    
    def __init__(self, event_type, **kwargs):
        self.type = event_type
        self.time = ticks_ms()
        
        # Adiciona todos os kwargs como atributos
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        attrs = []
        for key, value in self.__dict__.items():
            if key not in ['type', 'time']:
                attrs.append(f"{key}={value}")
        
        attr_str = f" ({', '.join(attrs)})" if attrs else ""
        return f"Event(type={self.type}{attr_str})"
    
    def __eq__(self, other):
        """Permite comparar eventos: if event.type == JOYSTICK_UP"""
        if isinstance(other, int):
            return self.type == other
        elif isinstance(other, Event):
            return self.type == other.type
        return False

class EventManager:
    """
    Gerenciador de eventos - Como pygame.event
    Detecta mudanças de estado do hardware e gera eventos
    """
    
    def __init__(self, debug=False):
        self.debug = debug
        self.event_queue = []
        
        # Estados anteriores para detectar mudanças
        self._last_states = {
            'joystick_dir': 'center',
            'joystick_button': False,
            'button_a': False,
            'button_b': False,
        }
        
        # Hardware references (será definido depois)
        self.joystick = None
        self.buttons = None
        
        # Configurações de debounce
        self.debounce_time = 100  # ms
        self._last_event_times = {}
        
    def init_hardware(self, joystick=None, buttons=None):
        """Inicializa referências do hardware"""
        self.joystick = joystick
        self.buttons = buttons
        
        if self.debug:
            print("EventManager: Hardware inicializado")
            if joystick:
                print(f"  Joystick: {joystick}")
            if buttons:
                print(f"  Botões: {buttons}")
    
    def _should_debounce(self, event_type):
        """Verifica se deve aplicar debounce ao evento"""
        current_time = ticks_ms()
        last_time = self._last_event_times.get(event_type, 0)
        
        if ticks_diff(current_time, last_time) < self.debounce_time:
            return True
            
        self._last_event_times[event_type] = current_time
        return False
    
    def _add_event(self, event_type, **kwargs):
        """Adiciona evento à fila com debounce"""
        if not self._should_debounce(event_type):
            event = Event(event_type, **kwargs)
            self.event_queue.append(event)
            
            if self.debug:
                print(f"Event: {event}")
    
    def poll(self):
        """
        Faz polling do hardware e gera eventos
        Deve ser chamado a cada frame - Como pygame.event.pump()
        """
        if not (self.joystick or self.buttons):
            return
            
        try:
            # === JOYSTICK ===
            if self.joystick:
                # Direção do joystick
                current_dir = self.joystick.get_direction()
                last_dir = self._last_states['joystick_dir']
                
                if current_dir != last_dir:
                    # Saiu de uma direção
                    if last_dir != 'center':
                        if last_dir in ['north', 'northeast', 'northwest']:
                            pass  # Não gera evento de "UP_UP" 
                        elif last_dir in ['south', 'southeast', 'southwest']:
                            pass  # Não gera evento de "DOWN_UP"
                    
                    # Entrou em nova direção
                    if current_dir != 'center':
                        norm_x, norm_y = self.joystick.get_normalized()
                        
                        if current_dir in ['north', 'northeast', 'northwest']:
                            self._add_event(JOYSTICK_UP, direction=current_dir, x=norm_x, y=norm_y)
                        elif current_dir in ['south', 'southeast', 'southwest']:
                            self._add_event(JOYSTICK_DOWN, direction=current_dir, x=norm_x, y=norm_y)
                        elif current_dir in ['east', 'northeast', 'southeast']:
                            self._add_event(JOYSTICK_RIGHT, direction=current_dir, x=norm_x, y=norm_y)
                        elif current_dir in ['west', 'northwest', 'southwest']:
                            self._add_event(JOYSTICK_LEFT, direction=current_dir, x=norm_x, y=norm_y)
                    else:
                        self._add_event(JOYSTICK_CENTER)
                        
                    self._last_states['joystick_dir'] = current_dir
                
                # Botão do joystick
                joy_btn_current = self.joystick.is_pressed()
                joy_btn_last = self._last_states['joystick_button']
                
                if joy_btn_current != joy_btn_last:
                    if joy_btn_current:
                        self._add_event(JOYSTICK_BUTTON_DOWN)
                    else:
                        self._add_event(JOYSTICK_BUTTON_UP)
                    self._last_states['joystick_button'] = joy_btn_current
            
            # === BOTÕES ===
            if self.buttons:
                # Botão A
                btn_a_current = self.buttons['a'].is_pressed() if 'a' in self.buttons else False
                btn_a_last = self._last_states['button_a']
                
                if btn_a_current != btn_a_last:
                    if btn_a_current:
                        self._add_event(BUTTON_A_DOWN)
                    else:
                        self._add_event(BUTTON_A_UP)
                    self._last_states['button_a'] = btn_a_current
                
                # Botão B
                btn_b_current = self.buttons['b'].is_pressed() if 'b' in self.buttons else False
                btn_b_last = self._last_states['button_b']
                
                if btn_b_current != btn_b_last:
                    if btn_b_current:
                        self._add_event(BUTTON_B_DOWN)
                    else:
                        self._add_event(BUTTON_B_UP)
                    self._last_states['button_b'] = btn_b_current
                        
        except Exception as e:
            if self.debug:
                print(f"EventManager: Erro no polling - {e}")
    
    def get(self):
        """
        Retorna lista de eventos e limpa a fila - Como pygame.event.get()
        
        Returns:
            List[Event]: Lista de eventos ocorridos desde último get()
        """
        events = self.event_queue.copy()
        self.event_queue.clear()
        return events
    
    def wait(self, timeout=None):
        """
        Espera por um evento - Como pygame.event.wait()
        
        Args:
            timeout: Timeout em milissegundos (None = infinito)
            
        Returns:
            Event: Primeiro evento que ocorrer
        """
        start_time = ticks_ms()
        
        while True:
            self.poll()
            events = self.get()
            
            if events:
                return events[0]
                
            if timeout and ticks_diff(ticks_ms(), start_time) > timeout:
                return None
                
            # Sleep curto para não consumir 100% CPU
            import time
            time.sleep_ms(10)
    
    def peek(self, event_types=None):
        """
        Olha eventos na fila sem removê-los - Como pygame.event.peek()
        
        Args:
            event_types: Lista de tipos a procurar ou None para todos
            
        Returns:
            bool: True se encontrou evento do tipo
        """
        if event_types is None:
            return len(self.event_queue) > 0
            
        if isinstance(event_types, int):
            event_types = [event_types]
            
        for event in self.event_queue:
            if event.type in event_types:
                return True
        return False
    
    def clear(self, event_types=None):
        """
        Limpa eventos da fila - Como pygame.event.clear()
        
        Args:
            event_types: Lista de tipos a limpar ou None para todos
        """
        if event_types is None:
            self.event_queue.clear()
        else:
            if isinstance(event_types, int):
                event_types = [event_types]
                
            self.event_queue = [e for e in self.event_queue if e.type not in event_types]
    
    def post(self, event):
        """
        Adiciona evento customizado à fila - Como pygame.event.post()
        
        Args:
            event: Event ou tipo de evento
        """
        if isinstance(event, int):
            event = Event(event)
        elif not isinstance(event, Event):
            raise ValueError("event deve ser Event ou int")
            
        self.event_queue.append(event)

# =============================================================================
# ALIASES PARA FACILITAR USO - Como Pygame
# =============================================================================

# Instância global do gerenciador (como pygame.event)
events = EventManager()

def init_events(joystick=None, buttons=None, debug=False):
    """
    Inicializa sistema de eventos
    
    Args:
        joystick: Instância do Joystick
        buttons: Dict com botões {'a': Button, 'b': Button}
        debug: Ativa debug
    """
    global events
    events.debug = debug
    events.init_hardware(joystick, buttons)

def get():
    """Retorna eventos - Como pygame.event.get()"""
    return events.get()

def poll():
    """Faz polling do hardware - Como pygame.event.pump()"""
    events.poll()

def wait(timeout=None):
    """Espera por evento - Como pygame.event.wait()"""
    return events.wait(timeout)

def peek(event_types=None):
    """Verifica se há eventos - Como pygame.event.peek()"""
    return events.peek(event_types)

def clear(event_types=None):
    """Limpa eventos - Como pygame.event.clear()"""
    events.clear(event_types)

def post(event):
    """Adiciona evento - Como pygame.event.post()"""
    events.post(event)

# =============================================================================
# CLASSE PARA GAME LOOP MANUAL
# =============================================================================

class GameLoop:
    """
    Classe para criar game loops manuais - Como Pygame/Godot
    """
    
    def __init__(self, fps=60):
        self.fps = fps
        self.frame_time = 1000 // fps
        self.running = False
        self.clock_time = 0
        
    def should_update(self):
        """Verifica se deve atualizar (controle de FPS)"""
        current_time = ticks_ms()
        if ticks_diff(current_time, self.clock_time) >= self.frame_time:
            self.clock_time = current_time
            return True
        return False
    
    def tick(self):
        """Atualiza o clock - Como pygame.time.Clock.tick()"""
        while not self.should_update():
            import time
            time.sleep_ms(1)
    
    def start(self):
        """Inicia o loop"""
        self.running = True
        self.clock_time = ticks_ms()
    
    def stop(self):
        """Para o loop"""
        self.running = False

# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    print("🎮 Demo Sistema de Eventos - BitDogLab V7")
    print("Exemplo de uso como Pygame/Godot")
    
    # Simula um game loop manual
    def demo_game_loop():
        print("\n=== GAME LOOP MANUAL ===")
        print("Use o joystick e botões!")
        print("Pressione ambos os botões para sair")
        
        try:
            # Inicializa hardware
            from joystick import Joystick
            from button import Button
            from config import PINS
            
            joystick = Joystick(
                pin_x=PINS.JOYSTICK_VRX,
                pin_y=PINS.JOYSTICK_VRY,
                pin_btn=PINS.JOYSTICK_BUTTON,
                deadzone_x=3000,
                deadzone_y=3000,
                invert_y=True
            )
            
            buttons = {
                'a': Button(PINS.BUTTON_A),
                'b': Button(PINS.BUTTON_B)
            }
            
            # Inicializa eventos
            init_events(joystick, buttons, debug=True)
            
            # Game loop
            clock = GameLoop(fps=30)
            clock.start()
            
            while clock.running:
                # Polling dos eventos (obrigatório)
                poll()
                
                # Processa eventos
                for event in get():
                    print(f"Evento: {event}")
                    
                    # Navegação
                    if event == JOYSTICK_UP:
                        print("  -> Mover para CIMA")
                    elif event == JOYSTICK_DOWN:
                        print("  -> Mover para BAIXO")
                    elif event == JOYSTICK_LEFT:
                        print("  -> Mover para ESQUERDA")
                    elif event == JOYSTICK_RIGHT:
                        print("  -> Mover para DIREITA")
                    elif event == JOYSTICK_CENTER:
                        print("  -> Joystick centralizado")
                    
                    # Botões
                    elif event == BUTTON_A_DOWN:
                        print("  -> Botão A pressionado")
                    elif event == BUTTON_A_UP:
                        print("  -> Botão A liberado")
                    elif event == BUTTON_B_DOWN:
                        print("  -> Botão B pressionado")
                    elif event == BUTTON_B_UP:
                        print("  -> Botão B liberado")
                    
                    # Sair (ambos os botões)
                    if (peek([BUTTON_A_DOWN]) and peek([BUTTON_B_DOWN])):
                        print("  -> SAINDO (ambos botões)")
                        clock.stop()
                
                # Controle de FPS
                clock.tick()
                
        except ImportError as e:
            print(f"Erro de import: {e}")
        except KeyboardInterrupt:
            print("\nDemo interrompido")
        except Exception as e:
            print(f"Erro: {e}")
    
    demo_game_loop()
    print("Demo finalizada!")
