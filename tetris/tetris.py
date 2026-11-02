import tkinter as tk
import random

# Configurações do jogo
TamanhoPeca = 30
LarguraTela, AlturaTela = 300, 600  # A altura foi aumentada para dar mais espaço
Cores = ['#b86100', '#b86100', '#8a5bb3', '#da00ff', '#cfc900', '#97ff00']
PecaShape = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]

# Função para criar a nova peça
def NovaPeca():
    shape = random.choice(PecaShape)
    color = random.choice(Cores)
    return {'shape': shape, 'color': color, 'x': 2, 'y': 0}

# Função para mover a peça
def MoverPeca(Peca, dx, dy):
    Peca['x'] += dx
    Peca['y'] += dy

# Função para rotacionar a peça
def RotacionaPeca(Peca):
    Peca['shape'] = [list(row) for row in zip(*Peca['shape'][::-1])]

# Função para desenhar o tabuleiro e a peça
def DesenhaTabuleiro():
    canvas.delete("all")  # Limpa a tela
    # Desenha as peças no tabuleiro
    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x]:
                canvas.create_rectangle(x * TamanhoPeca, y * TamanhoPeca,
                                        (x + 1) * TamanhoPeca, (y + 1) * TamanhoPeca,
                                        fill=board[y][x], outline="black")
    # Desenha a peça ativa
    for i, row in enumerate(Peca['shape']):
        for j, cell in enumerate(row):
            if cell:
                canvas.create_rectangle((Peca['x'] + j) * TamanhoPeca, (Peca['y'] + i) * TamanhoPeca,
                                        (Peca['x'] + j + 1) * TamanhoPeca, (Peca['y'] + i + 1) * TamanhoPeca,
                                        fill=Peca['color'], outline="black")

# Função para verificar se a posição da peça é válida
def PosicaoValida(Peca):
    for i, row in enumerate(Peca['shape']):
        for j, cell in enumerate(row):
            if cell:
                x, y = Peca['x'] + j, Peca['y'] + i
                if x < 0 or x >= LarguraTela // TamanhoPeca or y >= AlturaTela // TamanhoPeca or board[y][x]:
                    return False
    return True

# Função para adicionar a peça ao tabuleiro
def AdicionarNoTabuleiro():
    for i, row in enumerate(Peca['shape']):
        for j, cell in enumerate(row):
            if cell:
                x, y = Peca['x'] + j, Peca['y'] + i
                board[y][x] = Peca['color']

# Função para limpar as linhas completas
def LimparLinha():
    global score
    full_lines = [i for i, row in enumerate(board) if all(cell for cell in row)]
    for i in full_lines:
        board.pop(i)
        board.insert(0, [None] * (LarguraTela // TamanhoPeca))  # Adiciona linha vazia no topo
    score += len(full_lines)

# Função principal do jogo
def game_loop():
    global Peca, board, score, game_over
    if game_over:
        canvas.create_text(LarguraTela // 2, AlturaTela // 2, text="GAME OVER", font=("Arial", 30), fill="White")
        return
    # Mover a peça para baixo
    MoverPeca(Peca, 0, 1)
    if not PosicaoValida(Peca):
        MoverPeca(Peca, 0, -1)
        AdicionarNoTabuleiro()
        LimparLinha()
        Peca = NovaPeca()
        if not PosicaoValida(Peca):
            game_over = True
    DesenhaTabuleiro()
    root.after(500, game_loop)  # Repete o loop a cada 500 ms

# Função para movimentação da peça
def PressionaTecla(event):
    global Peca
    if event.keysym == "Left":
        MoverPeca(Peca, -1, 0)
        if not PosicaoValida(Peca):
            MoverPeca(Peca, 1, 0)
    elif event.keysym == "Right":
        MoverPeca(Peca, 1, 0)
        if not PosicaoValida(Peca):
            MoverPeca(Peca, -1, 0)
    elif event.keysym == "Down":
        MoverPeca(Peca, 0, 1)
        if not PosicaoValida(Peca):
            MoverPeca(Peca, 0, -1)
    elif event.keysym == "Up":
        RotacionaPeca(Peca)
        if not PosicaoValida(Peca):
            RotacionaPeca(Peca)
            RotacionaPeca(Peca)
            RotacionaPeca(Peca)

# Configurações da interface
root = tk.Tk()
root.title("TETRIS GAME")
canvas = tk.Canvas(root, width=LarguraTela, height=AlturaTela, bg="black")
canvas.pack()

# Variáveis do jogo
board = [[None] * (LarguraTela // TamanhoPeca) for _ in range(AlturaTela // TamanhoPeca)]  # Ajuste no tamanho
Peca = NovaPeca()
score = 0
game_over = False

root.bind("<KeyPress>", PressionaTecla)
game_loop()  # Inicia o loop do jogo
root.mainloop()