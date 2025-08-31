# Sistema de Áudio - Buzzer Module

## Estrutura de Arquivos

```
assets/audio/
├── ui/          # Sons de interface
├── game/        # Sons de jogo
├── sfx/         # Efeitos sonoros
└── music/       # Músicas (41 músicas do Arduino Songs + outras)
```

## Formato dos Arquivos de Som

### Sons Simples (UI, Game, SFX)
```
# Comentário
FREQUENCIA:DURACAO_MS:VOLUME
NOTA:DURACAO_MS:VOLUME
```

### Música (formato Arduino/Zelda)
```
# Comentário
# Tempo: 120 BPM
NOTA:DURACAO_TIPO
```

## Uso do Módulo

```python
from buzzer import buzzer, play_ui_sound, play_game_sound, play_sfx
from buzzer import play_music, list_available_music

# Tocar sons por categoria
play_ui_sound("click")
play_game_sound("coin_collect")
play_sfx("r2d2")

# Tocar músicas (detecta formato automaticamente)
play_music("escala")          # Formato simples
play_music("supermariobros")  # Formato Arduino (com BPM)
play_music("tetris")          # Formato Arduino

# Listar todas as músicas
list_available_music()

# Controle direto
buzzer.play_note(440, 0.5)  # 440Hz por 0.5 segundos
buzzer.play_note_with_fade(880, 3.0, fade_in_time=0.5, fade_out_time=0.5)
buzzer.fade_in(660, duration=1.0)
buzzer.fade_out(duration=1.0)

# Volume global
from buzzer import set_global_volume, get_global_volume, mute_all
set_global_volume(0.5)  # 50% do volume
mute_all()  # Silencia tudo
```

## Músicas Disponíveis (41 do Arduino Songs)

### Clássicas
- `asabranca.txt` - Asa Branca
- `brahmslullaby.txt` - Brahms Lullaby
- `cannonind.txt` - Cannon in D
- `furelise.txt` - Für Elise
- `greensleeves.txt` - Greensleeves
- `minuetg.txt` - Minuet in G
- `odetojoy.txt` - Ode to Joy
- `silentnight.txt` - Silent Night
- `thebadinerie.txt` - The Badinerie

### Games/Anime
- `bloodytears.txt` - Bloody Tears (Castlevania)
- `doom.txt` - Doom Theme
- `greenhill.txt` - Green Hill Zone (Sonic)
- `jigglypuffsong.txt` - Jigglypuff Song (Pokémon)
- `pacman.txt` - Pac-Man Theme
- `professorlayton.txt` - Professor Layton Theme
- `songofstorms.txt` - Song of Storms (Zelda)
- `supermariobros.txt` - Super Mario Bros
- `tetris.txt` - Tetris Theme
- `vampirekiller.txt` - Vampire Killer (Castlevania)
- `zeldaslullaby.txt` - Zelda's Lullaby
- `zeldatheme.txt` - Zelda Theme

### Movies/TV
- `cantinaband.txt` - Cantina Band (Star Wars)
- `gameofthrones.txt` - Game of Thrones Theme
- `harrypotter.txt` - Harry Potter Theme
- `imperialmarch.txt` - Imperial March (Star Wars)
- `pinkpanther.txt` - Pink Panther Theme
- `princeigor.txt` - Prince Igor
- `startrekintro.txt` - Star Trek Intro
- `starwars.txt` - Star Wars Main Theme
- `thegodfather.txt` - The Godfather Theme
- `thelionsleepstonight.txt` - The Lion Sleeps Tonight

### Pop/Rock
- `babyelephantwalk.txt` - Baby Elephant Walk
- `happybirthday.txt` - Happy Birthday
- `keyboardcat.txt` - Keyboard Cat
- `merrychristmas.txt` - Merry Christmas
- `nevergonnagiveyouup.txt` - Never Gonna Give You Up (Rick Roll)
- `takeonme.txt` - Take On Me (a-ha)
- `thelick.txt` - The Lick (Jazz)

### Outros
- `miichannel.txt` - Mii Channel (Nintendo Wii)
- `nokia.txt` - Nokia Ringtone
- `pulodagaita.txt` - Pulo da Gaita

### Sons Disponíveis

#### UI
- `click.txt` - Click de botão
- `hover.txt` - Hover de menu
- `error.txt` - Som de erro
- `success.txt` - Som de sucesso
- `blip.txt` - Blip rápido

#### Game
- `pause.txt` - Som de pausa
- `resume.txt` - Som de resume
- `coin_collect.txt` - Coletar moeda
- `power_up.txt` - Power up
- `power_down.txt` - Power down
- `level_complete.txt` - Level complete
- `game_over.txt` - Game over
- `victory.txt` - Vitória
- `health_low.txt` - Health baixa
- `countdown_tick.txt` - Tick do countdown
- `countdown_final.txt` - Final do countdown

#### SFX
- `r2d2.txt` - Som do R2D2
- `star_trek.txt` - Som do Star Trek
