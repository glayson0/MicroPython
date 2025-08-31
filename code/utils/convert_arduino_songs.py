#!/usr/bin/env python3
"""
Conversor de músicas do Arduino para o formato do nosso framework MicroPython
"""

import os
import re
import sys

def extract_melody_from_arduino(content):
    """Extrai a melodia e tempo de um arquivo Arduino .ino"""
    
    # Extrai o tempo
    tempo_match = re.search(r'int\s+tempo\s*=\s*(\d+)', content)
    tempo = int(tempo_match.group(1)) if tempo_match else 120
    
    # Encontra o array melody[] (várias variações possíveis)
    melody_patterns = [
        r'int\s+melody\[\]\s*=\s*\{(.*?)\};',
        r'const\s+int\s+melody\[\]\s*PROGMEM\s*=\s*\{(.*?)\};',
        r'const\s+int\s+melody\[\]\s*=\s*\{(.*?)\};',
    ]
    
    melody_match = None
    for pattern in melody_patterns:
        melody_match = re.search(pattern, content, re.DOTALL)
        if melody_match:
            break
    
    if not melody_match:
        return None, tempo
    
    melody_content = melody_match.group(1)
    
    # Remove comentários e quebras de linha
    melody_content = re.sub(r'//.*', '', melody_content)
    melody_content = re.sub(r'/\*.*?\*/', '', melody_content, flags=re.DOTALL)
    
    # Extrai pares de nota,duração
    note_pattern = r'(NOTE_[A-GS]+\d+|REST),\s*(-?\d+)'
    matches = re.findall(note_pattern, melody_content)
    
    result = []
    for note, duration in matches:
        result.append(f"{note}:{duration}")
    
    return result, tempo

def get_song_title(content):
    """Extrai o título da música do comentário inicial"""
    lines = content.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if line.startswith('/*') or line.startswith('*'):
            line = re.sub(r'^/\*\s*', '', line)
            line = re.sub(r'^\*\s*', '', line)
            line = line.strip()
            if line and not line.startswith('Connect') and not line.startswith('More songs'):
                return line
    return "Unknown Song"

def convert_song_file(arduino_file, output_dir):
    """Converte um arquivo .ino para nosso formato .txt"""
    
    try:
        with open(arduino_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"Erro ao ler {arduino_file}")
        return False
    
    melody, tempo = extract_melody_from_arduino(content)
    
    if not melody:
        print(f"Não foi possível extrair melodia de {arduino_file}")
        return False
    
    title = get_song_title(content)
    song_name = os.path.basename(os.path.dirname(arduino_file))
    
    # Cria o arquivo de saída
    output_file = os.path.join(output_dir, f"{song_name}.txt")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n")
            f.write(f"# Tempo: {tempo} BPM\n")
            f.write(f"# Convertido do Arduino Songs\n")
            f.write(f"# Formato: NOTA:DURAÇÃO\n\n")
            
            # Escreve as notas (8 por linha para melhor legibilidade)
            for i, note in enumerate(melody):
                if i > 0 and i % 8 == 0:
                    f.write('\n')
                f.write(note + ' ')
            f.write('\n')
        
        print(f"✓ Convertido: {song_name} -> {output_file}")
        return True
        
    except Exception as e:
        print(f"Erro ao salvar {output_file}: {e}")
        return False

def main():
    arduino_songs_dir = "/home/gnbo/bitdoglab/MicroPython/arduino-songs-master"
    output_dir = "/home/gnbo/bitdoglab/MicroPython/assets/audio/music"
    
    if not os.path.exists(arduino_songs_dir):
        print(f"Diretório não encontrado: {arduino_songs_dir}")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    converted = 0
    failed = 0
    
    print("=== Convertendo músicas do Arduino Songs ===\n")
    
    # Percorre todas as pastas
    for item in sorted(os.listdir(arduino_songs_dir)):
        item_path = os.path.join(arduino_songs_dir, item)
        
        if os.path.isdir(item_path):
            # Procura por arquivo .ino na pasta
            ino_files = [f for f in os.listdir(item_path) if f.endswith('.ino')]
            
            if ino_files:
                ino_file = os.path.join(item_path, ino_files[0])
                if convert_song_file(ino_file, output_dir):
                    converted += 1
                else:
                    failed += 1
    
    print(f"\n=== Conversão concluída ===")
    print(f"✓ Convertidas: {converted}")
    print(f"✗ Falharam: {failed}")
    print(f"📁 Arquivos salvos em: {output_dir}")

if __name__ == "__main__":
    main()
