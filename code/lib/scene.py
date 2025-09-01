import time
from lib.events import EventManager, init_events
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer  
from lib.joystick import Joystick
from lib.button import Button


class Scene:
    """
    Classe base para todas as cenas do sistema.
    
    Fornece funcionalidades básicas como:
    - Hardware compartilhado (display, buzzer, joystick, botões)
    - Sistema de navegação hierárquica
    - Gerenciamento de subcenas
    - Cleanup automático de recursos
    - Loop principal com eventos
    """
    
    def __init__(self, name, parent=None):
        """
        Inicializa uma nova cena.
        
        Args:
            name (str): Nome da cena
            parent (Scene): Cena pai (None para cena raiz)
        """
        self.name = name
        self.parent = parent
        self.subscenes = {}
        self.current_subscene = None
        self.running = False
        self.needs_render = True  # Controla quando precisa re-renderizar
        
        # Hardware compartilhado (inicializado na primeira cena)
        self.display = None
        self.buzzer = None
        self.joystick = None
        self.button_a = None
        self.button_b = None
        self.events = None
        
        # Inicializa hardware se for a primeira cena
        if parent is None:
            self.init_base_hardware()
        else:
            # Herda hardware da cena pai
            self.inherit_hardware(parent)
    
    def init_base_hardware(self):
        """Inicializa o hardware base compartilhado."""
        try:
            # Importa configurações do BitDogLab
            from config import PINS
            
            self.display = OLEDDisplay()
            self.buzzer = Buzzer(pin=PINS.BUZZER)
            self.joystick = Joystick(
                pin_x=PINS.JOYSTICK_VRX,
                pin_y=PINS.JOYSTICK_VRY,
                pin_btn=PINS.JOYSTICK_BUTTON,
                deadzone_x=3000,
                deadzone_y=3000,
                invert_y=True
            )
            self.button_a = Button(pin=PINS.BUTTON_A)
            self.button_b = Button(pin=PINS.BUTTON_B)
            
            # Inicializa sistema de eventos corretamente
            from lib.events import init_events
            buttons_dict = {'a': self.button_a, 'b': self.button_b}
            init_events(self.joystick, buttons_dict, debug=False)
            
            # O EventManager global já está inicializado pelo init_events
            from lib.events import events
            self.events = events
            
            print(f"Hardware inicializado para cena '{self.name}'")
        except Exception as e:
            print(f"Erro ao inicializar hardware: {e}")
            # Fallback sem hardware para permitir testes
            self.display = None
            self.buzzer = None
            self.joystick = None
            self.button_a = None
            self.button_b = None
            self.events = None
    
    def inherit_hardware(self, parent):
        """Herda hardware da cena pai."""
        self.display = parent.display
        self.buzzer = parent.buzzer
        self.joystick = parent.joystick
        self.button_a = parent.button_a
        self.button_b = parent.button_b
        self.events = parent.events
    
    def init_hardware(self):
        """
        Inicializa hardware específico da cena.
        Sobrescreva este método nas classes filhas para adicionar
        hardware específico (ex: LEDMatrix, sensores, etc).
        """
        pass
    
    def add_subscene(self, scene):
        """
        Adiciona uma subcena a esta cena.
        
        Args:
            scene (Scene): Subcena a ser adicionada
        """
        self.subscenes[scene.name] = scene
        scene.parent = self
        # Garante que a subcena tenha acesso ao hardware
        if hasattr(self, 'display') and self.display:
            scene.inherit_hardware(self)
    
    def goto_subscene(self, scene_name):
        """
        Navega para uma subcena.
        
        Args:
            scene_name (str): Nome da subcena
        """
        if scene_name in self.subscenes:
            self.current_subscene = self.subscenes[scene_name]
            self.current_subscene.run()
            # Quando volta da subcena, limpa a referência e marca para re-renderizar
            self.current_subscene = None
            self.needs_render = True
        else:
            print(f"Subcena '{scene_name}' não encontrada!")
    
    def goto_parent(self):
        """
        Volta para a cena pai (comportamento padrão do botão B).
        """
        if self.parent is not None:
            self.running = False
            print(f"Voltando de '{self.name}' para '{self.parent.name}'")
        else:
            if self.display:
                self.display.fill(0)
                self.display.text("Ate mais!...", 0, 0)
                self.display.show()
                self.display.fill(0)
            quit()

    def force_render(self):
        """Força re-renderização na próxima iteração do loop"""
        self.needs_render = True
    
    def render_standard_layout(self, title, items, selected_index, footer="A: OK == B: Back"):
        """
        Renderiza layout padrão: título, lista de 4 itens, rodapé
        
        Args:
            title (str): Título da tela
            items (list): Lista de itens para exibir
            selected_index (int): Índice do item selecionado
            footer (str): Texto do rodapé
        """
        if not self.display or not self.display.is_present:
            return
            
        lines = []
        
        # Linha 1: Título
        lines.append(title)
        lines.append("")  # Linha vazia
        
        # Linhas 3-6: Lista de 4 itens
        max_visible_items = 4
        
        if not items:
            # Se não há itens, mostra mensagem centralizada
            lines.extend([
                "",
                "  Nenhum item",
                "  encontrado!",
                ""
            ])
        else:
            # Calcula scroll offset para manter item selecionado visível
            scroll_offset = max(0, selected_index - max_visible_items + 1)
            if selected_index < max_visible_items:
                scroll_offset = 0
            
            # Mostra 4 itens
            for i in range(max_visible_items):
                item_idx = scroll_offset + i
                
                if item_idx < len(items):
                    item_text = str(items[item_idx])
                    
                    # Trunca se muito longo (18 caracteres para display pequeno)
                    if len(item_text) > 18:
                        item_text = item_text[:15] + "..."
                    
                    # Marca item selecionado com >
                    if item_idx == selected_index:
                        lines.append(f">{item_text}")
                    else:
                        lines.append(f" {item_text}")
                else:
                    lines.append("")  # Linha vazia se não há mais itens
        
        # Linha 7: Vazia
        lines.append("")
        
        # Linha 8: Rodapé
        lines.append(footer)
        
        # Renderiza com destaque
        self.render_with_highlight(lines)
    
    def render_with_highlight(self, lines):
        """Renderiza linhas com destaque para o item selecionado"""
        if not self.display or not self.display.is_present:
            return
            
        # Encontra linha com >
        highlight_line = -1
        
        for i, line in enumerate(lines):
            if line.startswith(">"):
                highlight_line = i
                lines[i] = " " + line[1:]  # Remove o marcador >
                break
        
        # Renderiza normalmente
        self.display.draw_lines(lines, valign='top')
        
        # Inverte a linha selecionada
        if highlight_line >= 0:
            self.display.invert_line(highlight_line)
            self.display.show()
    
    def render(self):
        """
        Renderiza a cena no display.
        Sobrescreva este método nas classes filhas.
        """
        if self.display:
            self.display.fill(0)
            self.display.text(f"Cena: {self.name}", 0, 0)
            self.display.text("A: Acao", 0, 20)
            self.display.text("B: Voltar", 0, 30)
            self.display.show()
    
    def handle_events(self):
        """
        Processa eventos da cena.
        Sobrescreva este método nas classes filhas para adicionar
        comportamentos específicos.
        """
        # Polling obrigatório dos eventos
        if self.events:
            from lib.events import poll
            poll()
        
        # Botão B sempre volta para cena pai (usando método direto do Button)
        if self.button_b and self.button_b.is_pressed():
            self.goto_parent()
            time.sleep(0.2)  # Debounce
    
    def update(self):
        """
        Atualiza lógica da cena.
        Sobrescreva este método nas classes filhas para adicionar
        lógica de atualização (animações, timers, etc).
        """
        pass
    
    def cleanup(self):
        """
        Limpa recursos da cena.
        Sobrescreva este método nas classes filhas para cleanup
        específico (parar música, desligar LEDs, etc).
        """
        pass
    
    def run(self):
        """
        Loop principal da cena.
        """
        print(f"Iniciando cena: {self.name}")
        
        # Inicializa hardware específico da cena
        self.init_hardware()
        
        self.running = True
        self.needs_render = True  # Força renderização inicial
        
        try:
            while self.running:
                # Renderiza apenas quando necessário
                if self.needs_render:
                    self.render()
                    self.needs_render = False
                
                # Processa eventos
                self.handle_events()
                
                # Atualiza lógica
                self.update()
                
                # Pausa menor para ser mais responsivo
                time.sleep(0.02)
                
        except KeyboardInterrupt:
            print(f"Interrompido: {self.name}")
        
        finally:
            # Sempre executa cleanup ao sair
            self.cleanup()
            print(f"Finalizando cena: {self.name}")


# Exemplo de uso básico:
if __name__ == "__main__":
    # Cria cena raiz
    menu_principal = Scene("Menu Principal")
    
    # Cria subcenas
    configuracoes = Scene("Configuracoes", menu_principal)
    jogos = Scene("Jogos", menu_principal)
    
    # Adiciona subcenas ao menu
    menu_principal.add_subscene(configuracoes)
    menu_principal.add_subscene(jogos)
    
    # Inicia o sistema
    menu_principal.run()
