"""
Menu Principal do BitDogLab V7
Sistema de cenas hierárquico simples
"""

from lib.scene import Scene
from src.app.gallery import Galeria
from src.app.media_player import MediaPlayer
from lib.events import *
from lib.buzzer import mute_all


class MenuPrincipal(Scene):
    """Menu principal com sistema de subcenas"""
    
    def __init__(self, name="Menu Principal", parent=None):
        super().__init__(name, parent)
        self.selected_option = 0
        self.options = [
            "1. Galeria",
            "2. Media Player", 
            "3. Configuracoes",
            "4. Sair"
        ]
        
        # Adiciona subcenas
        self.add_subscene(Galeria("Galeria", self))
        self.add_subscene(MediaPlayer("Media Player", self))
    
    def render(self):
        """Renderiza o menu usando layout padrão"""
        # Formata opções para exibição
        display_options = []
        for option in self.options:
            # Remove numeração se existir e formata
            if ". " in option:
                display_options.append(option.split(". ", 1)[1])
            else:
                display_options.append(option)
        
        # Usa renderização padrão
        self.render_standard_layout(
            title="====  MENU  ====",
            items=display_options,
            selected_index=self.selected_option,
            footer="= A:OK  B:Back ="
        )
    
    def handle_events(self):
        """Processa eventos do menu"""
        # Chama o método pai para eventos básicos (botão B = voltar)
        super().handle_events()
        
        # Processa eventos próprios se ainda rodando
        if not self.running:
            return
            
        # Usa as funções globais do sistema de eventos
        from lib.events import get, JOYSTICK_UP, JOYSTICK_DOWN, BUTTON_A_DOWN
        
        for event in get():
            # Navegação com joystick
            if event == JOYSTICK_UP:
                old_selection = self.selected_option
                self.selected_option = max(0, self.selected_option - 1)
                if old_selection != self.selected_option:
                    # self.play_navigation_sound()
                    self.needs_render = True  # Marca para re-renderizar
                    
            elif event == JOYSTICK_DOWN:
                old_selection = self.selected_option
                self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
                if old_selection != self.selected_option:
                    # self.play_navigation_sound()
                    self.needs_render = True  # Marca para re-renderizar
            
            # Seleção com botão A
            elif event == BUTTON_A_DOWN:
                self.handle_selection()
    
    def play_navigation_sound(self):
        """Som de navegação"""
        if self.buzzer:
            self.buzzer.play_note(600, 0.01)
    
    def handle_selection(self):
        """Processa seleção atual"""
        option = self.options[self.selected_option]
        
        # if self.buzzer:
        #     self.buzzer.play_note(1000, 0.05)
                
        if "Galeria" in option:
            self.goto_subscene("Galeria")
            
        elif "Media Player" in option:
            self.goto_subscene("Media Player")
            
        elif "Configuracoes" in option:
            print("-> Configuracoes (não implementado)")
            
        elif "Sair" in option:
            print("-> Saindo...")
            self.running = False
        
        # Força re-renderização após seleção
        self.needs_render = True


def main():
    """Função principal"""
    menu = MenuPrincipal()
    # mute_all()
    menu.run()


if __name__ == "__main__":
    main()
