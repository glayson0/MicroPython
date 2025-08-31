#!/usr/bin/env python3
"""
Script para converter arquivos do formato antigo para o formato Arduino/Zelda
"""

import os
import re

# Mapeamento de notas para frequências (reverso das constantes)
FREQ_TO_NOTE = {
    31: "NOTE_B0", 33: "NOTE_C1", 35: "NOTE_CS1", 37: "NOTE_D1", 39: "NOTE_DS1",
    41: "NOTE_E1", 44: "NOTE_F1", 46: "NOTE_FS1", 49: "NOTE_G1", 52: "NOTE_GS1",
    55: "NOTE_A1", 58: "NOTE_AS1", 62: "NOTE_B1", 65: "NOTE_C2", 69: "NOTE_CS2",
    73: "NOTE_D2", 78: "NOTE_DS2", 82: "NOTE_E2", 87: "NOTE_F2", 93: "NOTE_FS2",
    98: "NOTE_G2", 104: "NOTE_GS2", 110: "NOTE_A2", 117: "NOTE_AS2", 123: "NOTE_B2",
    131: "NOTE_C3", 139: "NOTE_CS3", 147: "NOTE_D3", 156: "NOTE_DS3", 165: "NOTE_E3",
    175: "NOTE_F3", 185: "NOTE_FS3", 196: "NOTE_G3", 208: "NOTE_GS3", 220: "NOTE_A3",
    233: "NOTE_AS3", 247: "NOTE_B3", 262: "NOTE_C4", 277: "NOTE_CS4", 294: "NOTE_D4",
    311: "NOTE_DS4", 330: "NOTE_E4", 349: "NOTE_F4", 370: "NOTE_FS4", 392: "NOTE_G4",
    415: "NOTE_GS4", 440: "NOTE_A4", 466: "NOTE_AS4", 494: "NOTE_B4", 523: "NOTE_C5",
    554: "NOTE_CS5", 587: "NOTE_D5", 622: "NOTE_DS5", 659: "NOTE_E5", 698: "NOTE_F5",
    740: "NOTE_FS5", 784: "NOTE_G5", 831: "NOTE_GS5", 880: "NOTE_A5", 932: "NOTE_AS5",
    988: "NOTE_B5", 1047: "NOTE_C6", 1109: "NOTE_CS6", 1175: "NOTE_D6", 1245: "NOTE_DS6",
    1319: "NOTE_E6", 1397: "NOTE_F6", 1480: "NOTE_FS6", 1568: "NOTE_G6", 1661: "NOTE_GS6",
    1760: "NOTE_A6", 1865: "NOTE_AS6", 1976: "NOTE_B6", 2093: "NOTE_C7", 2217: "NOTE_CS7",
    2349: "NOTE_D7", 2489: "NOTE_DS7", 2637: "NOTE_E7", 2794: "NOTE_F7", 2960: "NOTE_FS7",
    3136: "NOTE_G7", 3322: "NOTE_GS7", 3520: "NOTE_A7", 3729: "NOTE_AS7", 3951: "NOTE_B7",
    4186: "NOTE_C8", 4435: "NOTE_CS8", 4699: "NOTE_D8", 4978: "NOTE_DS8"
}

# Mapeamento de nomes de notas para constantes NOTE_
NOTE_NAMES = {
    'C': 'NOTE_C4', 'CS': 'NOTE_CS4', 'D': 'NOTE_D4', 'DS': 'NOTE_DS4',
    'E': 'NOTE_E4', 'F': 'NOTE_F4', 'FS': 'NOTE_FS4', 'G': 'NOTE_G4',
    'GS': 'NOTE_GS4', 'A': 'NOTE_A4', 'AS': 'NOTE_AS4', 'B': 'NOTE_B4',
    'C1': 'NOTE_C1', 'C2': 'NOTE_C2', 'C3': 'NOTE_C3', 'C4': 'NOTE_C4',
    'C5': 'NOTE_C5', 'C6': 'NOTE_C6', 'C7': 'NOTE_C7', 'C8': 'NOTE_C8',
    'D1': 'NOTE_D1', 'D2': 'NOTE_D2', 'D3': 'NOTE_D3', 'D4': 'NOTE_D4',
    'D5': 'NOTE_D5', 'D6': 'NOTE_D6', 'D7': 'NOTE_D7', 'D8': 'NOTE_D8',
    'E1': 'NOTE_E1', 'E2': 'NOTE_E2', 'E3': 'NOTE_E3', 'E4': 'NOTE_E4',
    'E5': 'NOTE_E5', 'E6': 'NOTE_E6', 'E7': 'NOTE_E7',
    'F1': 'NOTE_F1', 'F2': 'NOTE_F2', 'F3': 'NOTE_F3', 'F4': 'NOTE_F4',
    'F5': 'NOTE_F5', 'F6': 'NOTE_F6', 'F7': 'NOTE_F7',
    'G1': 'NOTE_G1', 'G2': 'NOTE_G2', 'G3': 'NOTE_G3', 'G4': 'NOTE_G4',
    'G5': 'NOTE_G5', 'G6': 'NOTE_G6', 'G7': 'NOTE_G7',
    'A1': 'NOTE_A1', 'A2': 'NOTE_A2', 'A3': 'NOTE_A3', 'A4': 'NOTE_A4',
    'A5': 'NOTE_A5', 'A6': 'NOTE_A6', 'A7': 'NOTE_A7',
    'B1': 'NOTE_B1', 'B2': 'NOTE_B2', 'B3': 'NOTE_B3', 'B4': 'NOTE_B4',
    'B5': 'NOTE_B5', 'B6': 'NOTE_B6', 'B7': 'NOTE_B7'
}

def freq_para_nota(freq):
    """Converte frequência para constante NOTE_XXX"""
    freq = int(freq)
    
    # Busca exata
    if freq in FREQ_TO_NOTE:
        return FREQ_TO_NOTE[freq]
    
    # Busca aproximada (diferença de até 5Hz)
    for f, note in FREQ_TO_NOTE.items():
        if abs(f - freq) <= 5:
            return note
    
    # Se não encontrar, retorna REST
    return "REST"

def nota_para_constante(note_name):
    """Converte nome de nota (ex: C5) para constante NOTE_XXX"""
    note_name = note_name.upper().strip()
    
    if note_name in NOTE_NAMES:
        return NOTE_NAMES[note_name]
    
    # Fallback para notas sem oitava especificada
    if note_name in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
        return NOTE_NAMES[f'{note_name}4']  # Assume oitava 4
    
    return "REST"

def converter_formato_antigo(content):
    """Converte formato antigo para formato Arduino"""
    lines = content.strip().split('\n')
    converted_lines = []
    converted_notes = []
    
    # Processa comentários e linhas
    for line in lines:
        line = line.strip()
        
        if line.startswith('#'):
            # Mantém comentários
            if 'Formato:' not in line:  # Remove linha do formato antigo
                converted_lines.append(line)
            continue
        
        if not line:
            continue
        
        # Processa linha de nota
        parts = line.split(':')
        if len(parts) < 2:
            continue
        
        note_or_freq = parts[0].strip()
        duration_ms = int(parts[1])
        
        # Converte para constante NOTE_XXX
        if note_or_freq.isdigit():
            # É frequência
            freq = int(note_or_freq)
            if freq == 0:
                note_const = "REST"
            else:
                note_const = freq_para_nota(freq)
        else:
            # É nome de nota
            note_const = nota_para_constante(note_or_freq)
        
        # Converte duração de ms para notação musical
        # Assumindo tempo 120 BPM: semibreve = 2000ms
        # 8 = colcheia (250ms), 4 = semínima (500ms), 2 = mínima (1000ms), 1 = semibreve (2000ms)
        if duration_ms <= 100:
            duration = 16  # semicolcheia
        elif duration_ms <= 200:
            duration = 8   # colcheia
        elif duration_ms <= 400:
            duration = 4   # semínima
        elif duration_ms <= 800:
            duration = 2   # mínima
        else:
            duration = 1   # semibreve
        
        converted_notes.append(f"{note_const}:{duration}")
    
    # Adiciona linha de tempo se não existir
    has_tempo = any('Tempo:' in line for line in converted_lines)
    if not has_tempo:
        converted_lines.append("# Tempo: 120 BPM")
    
    # Junta notas em uma linha
    if converted_notes:
        converted_lines.append(" ".join(converted_notes))
    
    return "\n".join(converted_lines)

def converter_arquivo(file_path):
    """Converte um arquivo do formato antigo"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Verifica se é formato antigo (tem FREQ:DURATION ou NOTE:DURATION:VOLUME)
        is_old_format = (
            ':' in content and 
            ('FREQ:DURATION' in content or 
             re.search(r'\d+:\d+:\d', content) or  # freq:duration:volume
             re.search(r'[A-G]\d*:\d+:', content))  # note:duration:volume
        )
        
        if not is_old_format:
            return False, "Já está no formato correto"
        
        converted_content = converter_formato_antigo(content)
        
        # Backup do arquivo original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Salva arquivo convertido
        with open(file_path, 'w') as f:
            f.write(converted_content)
        
        return True, "Convertido com sucesso"
        
    except Exception as e:
        return False, f"Erro: {str(e)}"

def converter_todos_arquivos():
    """Converte todos os arquivos que precisam de conversão"""
    base_path = "assets/audio"
    
    if not os.path.exists(base_path):
        print(f"❌ Diretório {base_path} não encontrado!")
        return
    
    arquivos_para_converter = []
    
    # Lista todos os arquivos .txt
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                arquivos_para_converter.append(file_path)
    
    print(f"🔄 Verificando {len(arquivos_para_converter)} arquivos...")
    print("=" * 60)
    
    convertidos = 0
    ja_corretos = 0
    erros = 0
    
    for file_path in arquivos_para_converter:
        rel_path = os.path.relpath(file_path, base_path)
        sucesso, msg = converter_arquivo(file_path)
        
        if sucesso:
            print(f"✅ {rel_path:<35} - {msg}")
            convertidos += 1
        elif "formato correto" in msg:
            print(f"✓  {rel_path:<35} - {msg}")
            ja_corretos += 1
        else:
            print(f"❌ {rel_path:<35} - {msg}")
            erros += 1
    
    print("=" * 60)
    print(f"📊 Resultado da conversão:")
    print(f"   Arquivos convertidos: {convertidos}")
    print(f"   Já estavam corretos: {ja_corretos}")
    print(f"   Erros: {erros}")
    print(f"   Total: {len(arquivos_para_converter)}")
    
    if convertidos > 0:
        print(f"\n💾 Backups criados com extensão .backup")
        print(f"📋 Execute verify_audio_format.py para verificar o resultado")

def main():
    print("🔄 Conversor de Formato de Arquivos de Áudio")
    print("Do formato antigo para o formato Arduino/Zelda")
    print()
    
    converter_todos_arquivos()

if __name__ == "__main__":
    main()
