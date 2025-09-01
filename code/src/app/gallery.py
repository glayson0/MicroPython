from lib.events import *
from lib.scene import Scene
from lib.oled import OLEDDisplay
from lib.buzzer import Buzzer
from lib.leds import LEDMatrix
from lib.joystick import Joystick
from lib.button import Button
from lib.config import PINS, PATTERNS_PATH
import os


class Galeria(Scene):
    """Explorador de arquivos em modo lista para patterns"""
    
    def __init__(self, name="Galeria", parent=None):
        super().__init__(name, parent)
        
        # Hardware específico da galeria
        self.matrix = None
        
        # Estado do explorador
        self.current_dir = PATTERNS_PATH
        self.files = []
        self.selected_index = 0
    
    def init_hardware(self):
        """Inicializa hardware da galeria"""
        super().init_hardware()  # Inicializa hardware base
        self.matrix = LEDMatrix()
        self.load_directory()
        self.buzzer = None  # Inicializado na cena pai
    
    def load_directory(self):
        """Carrega arquivos do diretório atual"""
        try:
            self.files = []
            
            # Adiciona opção para voltar se não estiver na raiz
            if self.current_dir != PATTERNS_PATH:
                self.files.append("../")
            
            # Lista arquivos .txt (exceto README)
            for file in os.listdir(self.current_dir):
                if file.endswith('.txt') and file != 'README.md':
                    self.files.append(file)
            
            # Ordena arquivos
            pattern_files = [f for f in self.files if not f.startswith("../")]
            pattern_files.sort()
            
            # Reconstrói lista com ../ no topo se existir
            self.files = []
            if self.current_dir != PATTERNS_PATH:
                self.files.append("../")
            self.files.extend(pattern_files)
            
            # Reset da seleção
            self.selected_index = 0
            
            # Carrega preview do primeiro arquivo se existir
            self.update_preview()
            
            print(f"Diretório carregado: {self.current_dir}")
            print(f"Arquivos: {self.files}")
                
        except Exception as e:
            print(f"Erro ao carregar diretório: {e}")
            self.files = []
    
    def update_preview(self):
        """Atualiza preview do arquivo selecionado na matriz"""
        if not self.matrix or not self.files or self.selected_index >= len(self.files):
            if self.matrix:
                self.matrix.clear()
            return
        
        selected_file = self.files[self.selected_index]
        
        # Se for diretório (.../), limpa matriz
        if selected_file.endswith("/"):
            self.matrix.clear()
            return
        
        try:
            pattern_name = selected_file.replace('.txt', '')
            self.matrix.set_pattern(pattern_name)
            self.matrix.draw()
        except Exception as e:
            print(f"Erro ao carregar preview {selected_file}: {e}")
            self.matrix.clear()
    
    def get_display_name(self, filename):
        """Formata nome do arquivo para exibição"""
        if filename == "../":
            return ".. (Voltar)"
        return filename.replace('.txt', '').replace('_', ' ')
    
    def render(self):
        """Renderiza interface da galeria usando layout padrão"""
        # Formata arquivos para exibição
        display_items = []
        for filename in self.files:
            display_items.append(self.get_display_name(filename))
        
        # Usa renderização padrão
        self.render_standard_layout(
            title="=== GALERIA ===",
            items=display_items,
            selected_index=self.selected_index,
            footer="= A:OK  B:Back ="
        )
    
    def navigate_up(self):
        """Navega para cima na lista"""
        if self.files and self.selected_index > 0:
            self.selected_index -= 1
            self.update_preview()
            if self.buzzer:
                self.buzzer.play_note(800, 0.03)
    
    def navigate_down(self):
        """Navega para baixo na lista"""
        if self.files and self.selected_index < len(self.files) - 1:
            self.selected_index += 1
            self.update_preview()
            if self.buzzer:
                self.buzzer.play_note(800, 0.03)
    
    def select_item(self):
        """Seleciona item atual"""
        if not self.files or self.selected_index >= len(self.files):
            return
        
        selected_file = self.files[self.selected_index]
        
        if selected_file == "../":
            # Voltar para diretório pai
            self.go_back()
        else:
            # Mostrar informações do arquivo
            self.show_file_info(selected_file)
    
    def go_back(self):
        """Volta para diretório pai ou sai da galeria"""
        if self.current_dir == PATTERNS_PATH:
            # Já na raiz, sair da galeria
            return False  # Sinaliza para sair
        else:
            # Voltar para diretório pai (implementação simples para MicroPython)
            if self.current_dir.endswith('/'):
                parent_parts = self.current_dir.rstrip('/').split('/')
            else:
                parent_parts = self.current_dir.split('/')
            
            if len(parent_parts) > 1:
                parent_dir = '/'.join(parent_parts[:-1]) + '/'
            else:
                parent_dir = PATTERNS_PATH
            
            self.current_dir = parent_dir
            self.load_directory()
            if self.buzzer:
                self.buzzer.play_note(600, 0.05)
            return True
    
    def show_file_info(self, filename):
        """Mostra informações detalhadas do arquivo"""
        pattern_name = filename.replace('.txt', '').replace('_', ' ')
        
        # Carrega informações do arquivo
        try:
            filepath = self.current_dir + filename
            with open(filepath, 'r') as f:
                content = f.read()
            
            lines_content = content.split('\n')
            pattern_lines = len([l for l in lines_content if l.strip() and not l.startswith('#')])
            file_size = len(content)
            
        except Exception as e:
            pattern_lines = 0
            file_size = 0
        
        info_lines = [
            f"=== {pattern_name.upper()} ===",
            "",
            f"Arquivo: {filename}",
            f"Linhas: {pattern_lines}",
            f"Bytes: {file_size}",
            "",
            "A:Voltar"
        ]
        
        if self.display:
            self.display.draw_lines(info_lines, valign='top')
        
        # Aguarda botão para voltar
        clock = GameLoop(fps=10)
        clock.start()
        
        while clock.running:
            poll()
            
            for event in get():
                if event == BUTTON_A_DOWN or event == BUTTON_B_DOWN:
                    clock.stop()
                    if self.buzzer:
                        self.buzzer.play_note(600, 0.05)
            
            clock.tick()
    
    def handle_events(self):
        """Processa eventos da galeria"""
        # Chama o método pai para eventos básicos (botão B = voltar)
        super().handle_events()
        
        # Processa eventos próprios se ainda rodando
        if not self.running:
            return
            
        # Usa as funções globais do sistema de eventos
        from lib.events import get, JOYSTICK_UP, JOYSTICK_DOWN, BUTTON_A_DOWN
        
        for event in get():
            if event == JOYSTICK_UP:
                self.navigate_up()
                self.needs_render = True  # Marca para re-renderizar
                
            elif event == JOYSTICK_DOWN:
                self.navigate_down()
                self.needs_render = True  # Marca para re-renderizar
                
            elif event == BUTTON_A_DOWN:
                # Selecionar item
                if self.buzzer:
                    self.buzzer.play_note(1000, 0.05)
                self.select_item()
                self.needs_render = True  # Marca para re-renderizar
    
    def cleanup(self):
        """Limpa recursos da galeria"""
        if self.matrix:
            self.matrix.clear()
        super().cleanup()


def galeria():
    """Função para executar a galeria"""
    app = Galeria()
    app.run()


# Execução direta
if __name__ == "__main__":
    galeria()
