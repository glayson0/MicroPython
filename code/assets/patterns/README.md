# Padrões para Matriz LED - BitDogLab V7

Esta pasta contém padrões visuais para a matriz de LEDs 5x5 do BitDogLab.

# Padrões para Matriz LED - BitDogLab V7

Esta pasta contém padrões visuais para a matriz de LEDs 5x5 do BitDogLab.

## Tipos de Padrões

### 1. Padrões Simples (monocromáticos)
Arquivos que usam X e . para definir apenas as posições dos LEDs.
A cor é especificada no código.

### 2. Padrões Coloridos (multicoloridos) 
Arquivos que usam números 0-9 para definir posições E cores dos LEDs.
As cores são definidas no próprio arquivo.

## Formato dos Arquivos

### Padrões Simples:
```
# Comentários começam com #
# Formato: 5x5 matriz
# X = LED aceso, . = LED apagado

..X..
.XXX.
XXXXX
..X..
..X..
```

### Padrões Coloridos:
```
# Comentários começam com #
# Formato: 5x5 matriz com cores
# 0 = LED apagado, 1-9 = cores diferentes

.121.
12321
12321
.121.
..1..

# Cores:
# 1: (255, 0, 0)     # Vermelho
# 2: (255, 100, 150) # Rosa
# 3: (255, 255, 255) # Branco
```

### Regras:
- **5 linhas**: Representam as linhas Y da matriz (0-4 de cima para baixo)
- **5 caracteres por linha**: Representam as colunas X (0-4 da esquerda para direita)
- **Padrões simples**: X = LED aceso, . = LED apagado
- **Padrões coloridos**: 0 = apagado, 1-9 = cores diferentes
- **#**: Comentários (linhas ignoradas)
- **Linhas vazias**: Ignoradas

### Cores RGB:
- Formato: `(R, G, B)` onde R, G, B são valores 0-255
- Exemplos: `(255, 0, 0)` = vermelho, `(0, 255, 0)` = verde, `(0, 0, 255)` = azul

### Exemplo de Uso:

```python
from ledmatrix import LEDMatrix, load_pattern

matrix = LEDMatrix(pin=7, num_leds=25)

# Padrão simples - especifica cor no código
pattern = load_pattern("assets/patterns/heart.txt")
matrix.set_pattern(pattern, (255, 0, 0))  # Coração vermelho
matrix.draw()

# Padrão colorido - cores vêm do arquivo
matrix.set_pattern("heart_color")  # Coração multicolorido
matrix.draw()
```

## Padrões Disponíveis

### Padrões Simples (monocromáticos):
- `heart.txt` - Coração
- `north.txt` - Seta para cima
- `south.txt` - Seta para baixo
- `east.txt` - Seta para direita
- `west.txt` - Seta para esquerda
- `smile.txt` - Rosto sorridente
- `plus.txt` - Cruz/Plus
- `circle.txt` - Círculo
- `square.txt` - Quadrado
- `x_mark.txt` - X grande
- `diamond.txt` - Losango
- `triangle_up.txt` - Triângulo para cima
- `checkerboard.txt` - Tabuleiro de xadrez

### Padrões Coloridos (multicoloridos):
- `heart_color.txt` - Coração multicolorido (vermelho/rosa/branco)
- `traffic_light.txt` - Semáforo (vermelho/amarelo/verde)
- `brazil_flag.txt` - Bandeira do Brasil (verde/amarelo/azul)
- `rainbow.txt` - Arco-íris horizontal (vermelho→azul)
- `fire.txt` - Chama de fogo (amarelo/laranja/vermelho)
- `rgb_grid.txt` - Grade RGB alternada
- `target.txt` - Alvo com anéis coloridos

## Criando Novos Padrões

### Padrão Simples:
1. Crie um arquivo `.txt` na pasta `patterns/`
2. Desenhe sua matriz 5x5 usando X e .
3. Adicione comentários explicativos
4. Use `matrix.set_pattern("nome", cor)` no código

### Padrão Colorido:
1. Crie um arquivo `.txt` na pasta `patterns/`
2. Desenhe sua matriz 5x5 usando números 0-9
3. Adicione seção `# Cores:` com definições RGB
4. Use `matrix.set_pattern("nome")` no código (sem especificar cor)

### Exemplo de Padrão Colorido:
```
# Meu padrão colorido
12321
23432
34543
23432
12321

# Cores:
# 1: (255, 0, 0)    # Vermelho
# 2: (255, 127, 0)  # Laranja  
# 3: (255, 255, 0)  # Amarelo
# 4: (0, 255, 0)    # Verde
# 5: (0, 0, 255)    # Azul
```
