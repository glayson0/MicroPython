#!/usr/bin/env python3
"""
Script para verificar e padronizar todos os arquivos de áudio 
para o formato único Arduino/Zelda
"""

import os
import re

def verificar_formato_arquivo(file_path):
    """Verifica se um arquivo está no formato Arduino/Zelda correto"""
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
        
        # Verifica se tem o padrão NOTE_XXX:duration
        pattern = r'NOTE_[A-GS]+\d*:-?\d+|REST:-?\d+'
        matches = re.findall(pattern, content)
        
        # Verifica se tem BPM (opcional)
        has_bpm = '# Tempo:' in content
        
        return {
            'format': 'arduino' if matches else 'unknown',
            'notes_count': len(matches),
            'has_bpm': has_bpm,
            'valid': len(matches) > 0
        }
    except Exception as e:
        return {
            'format': 'error',
            'error': str(e),
            'valid': False
        }

def listar_arquivos_audio(base_path):
    """Lista todos os arquivos .txt de áudio"""
    arquivos = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                categoria = os.path.basename(root)
                arquivos.append({
                    'path': file_path,
                    'name': file,
                    'category': categoria,
                    'relative_path': os.path.relpath(file_path, base_path)
                })
    
    return arquivos

def verificar_todos_arquivos():
    """Verifica todos os arquivos de áudio do projeto"""
    base_path = "assets/audio"
    
    if not os.path.exists(base_path):
        print(f"❌ Diretório {base_path} não encontrado!")
        return
    
    arquivos = listar_arquivos_audio(base_path)
    
    print(f"🔍 Verificando {len(arquivos)} arquivos de áudio...")
    print("=" * 60)
    
    stats = {
        'total': len(arquivos),
        'validos': 0,
        'invalidos': 0,
        'com_bpm': 0,
        'sem_bpm': 0
    }
    
    for arquivo in arquivos:
        info = verificar_formato_arquivo(arquivo['path'])
        categoria = arquivo['category']
        nome = arquivo['name']
        
        if info['valid']:
            status = "✅"
            stats['validos'] += 1
            if info['has_bpm']:
                stats['com_bpm'] += 1
            else:
                stats['sem_bpm'] += 1
        else:
            status = "❌"
            stats['invalidos'] += 1
        
        bpm_info = "BPM ✓" if info.get('has_bpm') else "BPM ✗"
        notes_count = info.get('notes_count', 0)
        
        print(f"{status} {categoria:>10}/{nome:<25} {notes_count:>3} notas {bpm_info}")
        
        if not info['valid'] and 'error' in info:
            print(f"    Erro: {info['error']}")
    
    print("=" * 60)
    print(f"📊 Estatísticas:")
    print(f"   Total de arquivos: {stats['total']}")
    print(f"   Válidos: {stats['validos']} ✅")
    print(f"   Inválidos: {stats['invalidos']} ❌")
    print(f"   Com BPM: {stats['com_bpm']}")
    print(f"   Sem BPM: {stats['sem_bpm']}")
    
    if stats['invalidos'] == 0:
        print("\n🎉 Todos os arquivos estão no formato correto!")
    else:
        print(f"\n⚠️  {stats['invalidos']} arquivos precisam ser corrigidos")

def mostrar_exemplo_arquivo():
    """Mostra um exemplo de arquivo válido"""
    print("\n📄 Exemplo de arquivo válido:")
    print("-" * 40)
    exemplo = """# Nokia Ringtone
# Tempo: 180 BPM
NOTE_E5:8 NOTE_D5:8 NOTE_FS4:4 NOTE_GS4:4
NOTE_CS5:8 NOTE_B4:8 NOTE_D4:4 NOTE_E4:4
NOTE_B4:8 NOTE_A4:8 NOTE_CS4:4 NOTE_E4:4
NOTE_A4:2"""
    print(exemplo)
    print("-" * 40)

def main():
    print("🎵 Verificador de Formato de Arquivos de Áudio")
    print("Sistema de Buzzer Simplificado")
    print()
    
    verificar_todos_arquivos()
    mostrar_exemplo_arquivo()
    
    print("\n📚 Documentação completa em: lib/README_buzzer.md")

if __name__ == "__main__":
    main()
