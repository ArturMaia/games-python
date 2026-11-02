import tkinter as tk
import random

# Definir as cores
COR_FUNDO = "#000000"
COR_SNAKE = "#00FF00"
COR_COMIDA = "#FF0000"

# Configurações do jogo
TAMANHO_CELULA = 20
LARGURA = 400
ALTURA = 400

class JogoSnake:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo Snake")
        
        # Configuração da tela de jogo
        self.canvas = tk.Canvas(self.root, width=LARGURA, height=ALTURA, bg=COR_FUNDO)
        self.canvas.pack()

        # Inicializando o estado do jogo
        self.snake = [(100, 100), (80, 100), (60, 100)]  # Posições iniciais da cobra
        self.direcao = "Direita"  # Direção inicial
        self.comida = None  # A comida será gerada aleatoriamente
        self.pontuacao = 0  # Pontuação inicial

        # Exibindo a pontuação
        self.label_pontuacao = tk.Label(self.root, text="Pontuação: 0", font=("Arial", 14))
        self.label_pontuacao.pack()

        # Teclas para controlar a direção
        self.root.bind("<Left>", self.mover_esquerda)
        self.root.bind("<Right>", self.mover_direita)
        self.root.bind("<Up>", self.mover_cima)
        self.root.bind("<Down>", self.mover_baixo)

        # Iniciar o jogo
        self.criar_comida()
        self.atualizar_jogo()

    def criar_comida(self):
        """Gerar a comida em uma posição aleatória que não colida com a cobra"""
        while True:
            x = random.randint(0, (LARGURA - TAMANHO_CELULA) // TAMANHO_CELULA) * TAMANHO_CELULA
            y = random.randint(0, (ALTURA - TAMANHO_CELULA) // TAMANHO_CELULA) * TAMANHO_CELULA
            if (x, y) not in self.snake:
                self.comida = (x, y)
                break

    def mover_esquerda(self, event):
        if self.direcao != "Direita":
            self.direcao = "Esquerda"

    def mover_direita(self, event):
        if self.direcao != "Esquerda":
            self.direcao = "Direita"

    def mover_cima(self, event):
        if self.direcao != "Baixo":
            self.direcao = "Cima"

    def mover_baixo(self, event):
        if self.direcao != "Cima":
            self.direcao = "Baixo"

    def atualizar_jogo(self):
        # Calcular a nova cabeça da cobra com base na direção
        cabeca_x, cabeca_y = self.snake[0]
        
        if self.direcao == "Direita":
            cabeca_x += TAMANHO_CELULA
        elif self.direcao == "Esquerda":
            cabeca_x -= TAMANHO_CELULA
        elif self.direcao == "Cima":
            cabeca_y -= TAMANHO_CELULA
        elif self.direcao == "Baixo":
            cabeca_y += TAMANHO_CELULA

        nova_cabeca = (cabeca_x, cabeca_y)

        # Verificar colisões
        if cabeca_x < 0 or cabeca_x >= LARGURA or cabeca_y < 0 or cabeca_y >= ALTURA or nova_cabeca in self.snake:
            self.game_over()
            return

        # Adicionar a nova cabeça à cobra
        self.snake = [nova_cabeca] + self.snake

        # Verificar se a cobra comeu a comida
        if nova_cabeca == self.comida:
            self.pontuacao += 1
            self.label_pontuacao.config(text=f"Pontuação: {self.pontuacao}")
            self.criar_comida()
        else:
            # Remover a cauda da cobra (apenas se não comeu)
            self.snake.pop()

        self.redesenhar_jogo()

        # Chamar novamente a função após 100ms
        self.root.after(100, self.atualizar_jogo)

    def redesenhar_jogo(self):
        """Redesenha a tela do jogo (cobra e comida)"""
        self.canvas.delete("all")

        # Desenhar a cobra
        for segmento in self.snake:
            self.canvas.create_rectangle(segmento[0], segmento[1], segmento[0] + TAMANHO_CELULA, segmento[1] + TAMANHO_CELULA, fill=COR_SNAKE)

        # Desenhar a comida
        self.canvas.create_oval(self.comida[0], self.comida[1], self.comida[0] + TAMANHO_CELULA, self.comida[1] + TAMANHO_CELULA, fill=COR_COMIDA)

    def game_over(self):
        """Exibe a tela de game over"""
        self.canvas.delete("all")
        self.canvas.create_text(LARGURA // 2, ALTURA // 2, text="Game Over", fill="white", font=("Arial", 24))
        self.canvas.create_text(LARGURA // 2, ALTURA // 2 + 30, text=f"Pontuação final: {self.pontuacao}", fill="white", font=("Arial", 16))

        # Finalizar o jogo após 2 segundos
        self.root.after(2000, self.root.quit)

if __name__ == "__main__":
    # Criar a janela principal
    root = tk.Tk()
    jogo = JogoSnake(root)
    root.mainloop()
