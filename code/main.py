"""
Exemplo de Menu com Sistema de Eventos Manual
Inspirado no Pygame/Godot - Você controla o loop!
"""

from lib.events import *
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer
from lib.joystick import Joystick
from lib.button import Button
from lib.config import PINS

class MenuManual:
    """Menu com controle manual do loop de eventos"""
    
    def __init__(self):
        self.selected_option = 0
        self.options = [
            "1. Galeria",
            "2. Media Player", 
            "3. Configurações",
            "4. Sair"
        ]
        self.running = False
        
        # Hardware
        self.display = None
        self.buzzer = None
        
    def init_hardware(self):
        """Inicializa hardware"""
        print("Inicializando hardware...")
        
        # Display
        self.display = OLEDDisplay()
        print(f"Display: {self.display}")
        
        # Buzzer
        self.buzzer = Buzzer(PINS.BUZZER)
        print(f"Buzzer: {self.buzzer}")
        
        # Joystick e botões
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
        
        # Inicializa sistema de eventos
        init_events(joystick, buttons, debug=True)
        
        print("Hardware inicializado!")
        
    def render(self):
        """Renderiza o menu"""
        if not self.display or not self.display.is_present:
            return
            
        lines = []
        lines.append("=== BitDogLab V7 ===")
        lines.append("")
        
        # Opções do menu
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                lines.append(f"> {option}")
            else:
                lines.append(f"  {option}")
        
        lines.append("")
        lines.append("Joy: Navegar")
        lines.append("A: Selecionar")
        
        self.display.draw_lines(lines, valign='middle')
        
    def play_navigation_sound(self):
        """Som de navegação"""
        if self.buzzer:
            self.buzzer.play_note(600, 0.1)
    
    def play_selection_sound(self):
        """Som de seleção"""
        if self.buzzer:
            self.buzzer.play_note(1000, 0.15)
    
    def handle_selection(self):
        """Processa seleção atual"""
        option = self.options[self.selected_option]
        self.play_selection_sound()
        
        print(f"Selecionado: {option}")
        
        if "Galeria" in option:
            print("-> Abrir Galeria (não implementado)")
            
        elif "Media Player" in option:
            print("-> Abrir Media Player (não implementado)")
            
        elif "Configurações" in option:
            print("-> Abrir Configurações (não implementado)")
            
        elif "Sair" in option:
            print("-> Saindo...")
            self.running = False
    
    def run(self):
        """
        Loop principal do menu - VOCÊ CONTROLA TUDO!
        Como Pygame/Godot
        """
        print("🎮 Menu Manual - BitDogLab V7")
        print("Sistema de eventos como Pygame/Godot")
        
        # Inicializa
        self.init_hardware()
        
        # Clock para controle de FPS
        clock = GameLoop(fps=15)
        clock.start()
        self.running = True
        
        # Renderização inicial
        self.render()
        
        try:
            # LOOP PRINCIPAL - VOCÊ CONTROLA!
            while self.running and clock.running:
                
                # 1. POLLING DOS EVENTOS (obrigatório a cada frame)
                poll()
                
                # 2. PROCESSA EVENTOS
                for event in get():
                    print(f"Evento: {event}")
                    
                    # Navegação com joystick
                    if event == JOYSTICK_UP:
                        old_selection = self.selected_option
                        self.selected_option = max(0, self.selected_option - 1)
                        if old_selection != self.selected_option:
                            self.play_navigation_sound()
                            self.render()
                            
                    elif event == JOYSTICK_DOWN:
                        old_selection = self.selected_option
                        self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
                        if old_selection != self.selected_option:
                            self.play_navigation_sound()
                            self.render()
                    
                    # Seleção com botão A
                    elif event == BUTTON_A_DOWN:
                        self.handle_selection()
                    
                    # Navegação alternativa com botão B
                    elif event == BUTTON_B_DOWN:
                        old_selection = self.selected_option
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                        if old_selection != self.selected_option:
                            self.play_navigation_sound()
                            self.render()
                
                # 3. AQUI VOCÊ PODE ADICIONAR SUA LÓGICA DE UPDATE
                # update_game_logic()
                # update_animations()
                # etc...
                
                # 4. CONTROLE DE FPS
                clock.tick()
                
        except KeyboardInterrupt:
            print("\nMenu interrompido pelo usuário")
        except Exception as e:
            print(f"Erro no menu: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Menu finalizado!")
            if self.display:
                self.display.clear()

def main():
    """Função principal"""
    menu = MenuManual()
    menu.run()

if __name__ == "__main__":
    main()
