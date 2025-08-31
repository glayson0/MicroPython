"""
Teste Básico do Sistema de Eventos
Exemplo mínimo de como usar o sistema como Pygame
"""

# Imports no topo
from lib.events import *
from lib.joystick import Joystick
from lib.button import Button
from lib.config import PINS

def teste_eventos_simples():
    """Teste básico dos eventos"""
    print("=== TESTE EVENTOS SIMPLES ===")
    
    try:
        # Inicializa hardware
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
        
        print("Hardware inicializado!")
        print("Use joystick e botões. Pressione A+B para sair.")
        print()
        
        # Variáveis de teste
        position_x = 5
        position_y = 3
        counter = 0
        
        # Game loop manual
        clock = GameLoop(fps=20)
        clock.start()
        
        while clock.running:
            
            # 1. POLLING (obrigatório)
            poll()
            
            # 2. EVENTOS
            for event in get():
                
                # Movimento do "cursor"
                if event == JOYSTICK_UP:
                    position_y = max(0, position_y - 1)
                    print(f"Cursor: ({position_x}, {position_y})")
                    
                elif event == JOYSTICK_DOWN:
                    position_y = min(7, position_y + 1)
                    print(f"Cursor: ({position_x}, {position_y})")
                    
                elif event == JOYSTICK_LEFT:
                    position_x = max(0, position_x - 1)
                    print(f"Cursor: ({position_x}, {position_y})")
                    
                elif event == JOYSTICK_RIGHT:
                    position_x = min(15, position_x + 1)
                    print(f"Cursor: ({position_x}, {position_y})")
                
                # Botões
                elif event == BUTTON_A_DOWN:
                    counter += 1
                    print(f"Botão A! Counter: {counter}")
                    
                elif event == BUTTON_B_DOWN:
                    counter -= 1
                    print(f"Botão B! Counter: {counter}")
            
            # 3. CONDIÇÃO DE SAÍDA
            # Verifica se ambos os botões estão pressionados
            if peek([BUTTON_A_DOWN]) and peek([BUTTON_B_DOWN]):
                print("Ambos botões - SAINDO!")
                clock.stop()
            
            # 4. FPS
            clock.tick()
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_eventos_simples()
