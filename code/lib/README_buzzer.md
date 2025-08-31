# Buzzer Module - Sistema de Áudio Simplificado

Este módulo fornece um sistema simples e genérico para tocar arquivos de áudio no buzzer do MicroPython.

## Características Principais

- **Um formato único**: Todos os arquivos de áudio usam o formato Arduino/Zelda
- **Função genérica**: Uma única função `play_audio()` para tocar qualquer arquivo
- **Controle modular**: Especifica o pino do buzzer, volume e loop para cada chamada
- **Sem dependências externas**: Funciona apenas com o arquivo de áudio

## Formato dos Arquivos de Áudio (.txt)

```txt
# Comentários começam com #
# Tempo: 120 BPM (opcional, padrão é 120)
NOTE_C4:4 NOTE_D4:4 NOTE_E4:2 REST:4
NOTE_F4:8 NOTE_G4:8 NOTE_A4:1
```

### Elementos do formato:
- **NOTE_XXX**: Nota musical (ex: NOTE_C4, NOTE_A4, etc.)
- **REST**: Silêncio
- **:X**: Duração da nota (1=semibreve, 2=mínima, 4=semínima, 8=colcheia, etc.)
- **Duração negativa (-4)**: Nota pontuada (50% mais longa)

## Como Usar

### Função Principal

```python
from lib.buzzer import play_audio

# Toca um arquivo uma vez
play_audio(pin=21, file_path="assets/audio/music/nokia.txt", volume=0.5)

# Toca em loop
play_audio(pin=21, file_path="assets/audio/music/nokia.txt", volume=0.3, loop=True)
```

### Classe Buzzer (para uso avançado)

```python
from lib.buzzer import Buzzer

buzzer = Buzzer(pin=21, default_volume=0.3)

# Toca uma nota individual
buzzer.play_note(440, duration=0.5, volume=0.3)

# Toca um arquivo
buzzer.play_audio_file("assets/audio/music/mario.txt", volume=0.5)

# Fade in/out
buzzer.play_note_with_fade(440, duration=3.0, fade_in_time=0.5, fade_out_time=0.5)

buzzer.stop()
```

### Controle de Volume Global

```python
from lib.buzzer import set_global_volume, get_global_volume, mute_all

# Define volume global (afeta todos os sons)
set_global_volume(0.5)

# Verifica volume atual
print(get_global_volume())

# Silencia tudo
mute_all()
```

## Parâmetros

### play_audio(pin, file_path, volume=0.3, loop=False)
- **pin**: Número do pino do buzzer (ex: 21)
- **file_path**: Caminho para o arquivo .txt
- **volume**: Volume de 0.0 a 1.0 (padrão: 0.3)
- **loop**: Se True, toca em loop contínuo (padrão: False)

## Notas Musicais Disponíveis

O módulo suporta todas as notas do arquivo `music_notes.py`:

```python
NOTE_B0, NOTE_C1, NOTE_CS1, NOTE_D1, NOTE_DS1, NOTE_E1, NOTE_F1, NOTE_FS1, NOTE_G1, NOTE_GS1, NOTE_A1, NOTE_AS1, NOTE_B1,
NOTE_C2, NOTE_CS2, NOTE_D2, NOTE_DS2, NOTE_E2, NOTE_F2, NOTE_FS2, NOTE_G2, NOTE_GS2, NOTE_A2, NOTE_AS2, NOTE_B2,
NOTE_C3, NOTE_CS3, NOTE_D3, NOTE_DS3, NOTE_E3, NOTE_F3, NOTE_FS3, NOTE_G3, NOTE_GS3, NOTE_A3, NOTE_AS3, NOTE_B3,
NOTE_C4, NOTE_CS4, NOTE_D4, NOTE_DS4, NOTE_E4, NOTE_F4, NOTE_FS4, NOTE_G4, NOTE_GS4, NOTE_A4, NOTE_AS4, NOTE_B4,
NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5,
NOTE_C6, NOTE_CS6, NOTE_D6, NOTE_DS6, NOTE_E6, NOTE_F6, NOTE_FS6, NOTE_G6, NOTE_GS6, NOTE_A6, NOTE_AS6, NOTE_B6,
NOTE_C7, NOTE_CS7, NOTE_D7, NOTE_DS7, NOTE_E7, NOTE_F7, NOTE_FS7, NOTE_G7, NOTE_GS7, NOTE_A7, NOTE_AS7, NOTE_B7,
NOTE_C8, NOTE_CS8, NOTE_D8, NOTE_DS8, REST
```

## Exemplos de Arquivos de Áudio

### Nokia Ringtone
```txt
# Tempo: 180 BPM
NOTE_E5:8 NOTE_D5:8 NOTE_FS4:4 NOTE_GS4:4
NOTE_CS5:8 NOTE_B4:8 NOTE_D4:4 NOTE_E4:4
NOTE_B4:8 NOTE_A4:8 NOTE_CS4:4 NOTE_E4:4
NOTE_A4:2
```

### Happy Birthday
```txt
# Tempo: 120 BPM
NOTE_C4:4 NOTE_C4:8 NOTE_D4:4 NOTE_C4:4 NOTE_F4:4 NOTE_E4:2
NOTE_C4:4 NOTE_C4:8 NOTE_D4:4 NOTE_C4:4 NOTE_G4:4 NOTE_F4:2
NOTE_C4:4 NOTE_C4:8 NOTE_C5:4 NOTE_A4:4 NOTE_F4:4 NOTE_E4:4 NOTE_D4:4
NOTE_AS4:4 NOTE_AS4:8 NOTE_A4:4 NOTE_F4:4 NOTE_G4:4 NOTE_F4:2
```

## Vantagens do Sistema Simplificado

1. **Simplicidade**: Uma única função para tocar qualquer arquivo
2. **Flexibilidade**: Pode especificar pino, volume e loop para cada chamada
3. **Modularidade**: Não depende de instâncias globais ou caminhos fixos
4. **Eficiência**: Sem código desnecessário para diferentes formatos
5. **Clareza**: API limpa e fácil de entender

## Migração de Código Antigo

**Antes:**
```python
from lib.buzzer import play_music, play_ui_sound, buzzer

play_music("nokia", volume=0.5)
play_ui_sound("click")
buzzer.play_audio_file(path, volume)
```

**Depois:**
```python
from lib.buzzer import play_audio

play_audio(21, "assets/audio/music/nokia.txt", volume=0.5)
play_audio(21, "assets/audio/ui/click.txt")
play_audio(21, path, volume)
```
