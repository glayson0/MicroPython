"""
Dicionário de Cenas - BitDogLab V7
Sistema simples de organização de aplicações
"""

from src.app.gallery import Galeria
from src.app.media_player import MediaPlayer

# Dicionário simples: nome da cena -> classe da aplicação
SCENES = {
    "galeria": Galeria,
    "media_player": MediaPlayer
}

# Funções utilitárias
def get_scene(scene_name):
    """Retorna a classe de uma cena"""
    return SCENES.get(scene_name)

def list_scenes():
    """Lista todas as cenas disponíveis"""
    return list(SCENES.keys())

def run_scene(scene_name):
    """Executa uma cena diretamente"""
    if scene_name in SCENES:
        scene_class = SCENES[scene_name]
        scene_instance = scene_class()
        scene_instance.run()
        return True
    return False
