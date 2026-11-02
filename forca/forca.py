import tkinter as tk
import random

# Função para gerar o tema
def Temas():
    tema = ['Filme', 'Comida', 'País']
    roleta = random.choice(tema)
    return roleta

# Função que gera a palavra com base no tema
def palavra(tema):
    if tema == 'País':
        paises = ['Brasil', 'Angola', 'Jamaica', 'Peru', 'Argentina']
        return random.choice(paises).lower()
    elif tema == 'Filme':
        filmes = ['Shrek', 'Carandiru', 'Toy Story', 'Titanic', 'Besouro']
        return random.choice(filmes).lower()
    elif tema == 'Comida':
        comidas = ['Feijoada', 'Pizza', 'Lasanha', 'Caruru', 'Sopa']
        return random.choice(comidas).lower()

# Função para iniciar o jogo
def iniciar_jogo():
    global palavra_secreta, letras_descobertas, chances, letras_erradas, tema
    
    tema = Temas()  # Gera o tema
    palavra_secreta = palavra(tema)  # Gera a palavra secreta com base no tema

    letras_descobertas = ['_' for _ in palavra_secreta]  # Lista para mostrar as letras descobertas
    chances = 6  # Número de chances
    letras_erradas = []  # Lista para letras erradas
    
    # Atualiza a interface com o tema e o estado inicial
    resultado_label.config(text="", fg="black")  # Limpa a mensagem de resultado
    atualizar_interface()

# Função para atualizar a interface
def atualizar_interface():
    global palavra_secreta, letras_descobertas, chances, letras_erradas, tema

    # Atualiza o rótulo do tema
    tema_label.config(text=f"Tema: {tema}")
    
    # Atualiza a palavra oculta
    palavra_label.config(text=" ".join(letras_descobertas))
    
    # Atualiza as chances
    chances_label.config(text=f"Chances restantes: {chances}")
    
    # Atualiza as letras erradas
    letras_erradas_label.config(text=f"Letras erradas: {', '.join(letras_erradas)}")
    
    # Verifica se o jogador ganhou ou perdeu
    if "_" not in letras_descobertas:
        resultado_label.config(text=f"Você venceu! A palavra era: {palavra_secreta}", fg="green")
    elif chances <= 0:
        resultado_label.config(text=f"Você perdeu! A palavra era: {palavra_secreta}", fg="red")

# Função para capturar a tentativa do jogador
def tentar_letra():
    global palavra_secreta, letras_descobertas, chances, letras_erradas
    
    letra = entrada_letra.get().lower()
    entrada_letra.delete(0, tk.END)  # Limpa o campo de entrada
    
    if len(letra) != 1 or not letra.isalpha():
        return  # Se a entrada não for uma única letra válida, não faz nada
    
    if letra in letras_erradas or letra in letras_descobertas:
        return  # Se a letra já foi tentada, não faz nada

    if letra in palavra_secreta:
        # Atualiza a lista de letras descobertas
        for i, char in enumerate(palavra_secreta):
            if char == letra:
                letras_descobertas[i] = letra
    else:
        # Se a letra estiver errada, diminui as chances
        chances -= 1
        letras_erradas.append(letra)
    
    # Atualiza a interface com o novo estado
    atualizar_interface()

# Criando a janela principal
root = tk.Tk()
root.title("Jogo da Forca")

# Aumentando o tamanho da tela para 800x600 e definindo o fundo cinza
root.geometry("400x650")
root.config(bg="#D3D3D3")  # Cor de fundo cinza claro

# Configuração da interface
tema_label = tk.Label(root, text="Tema: ", font=("Arial", 18), bg="#D3D3D3")
tema_label.pack(pady=20)

palavra_label = tk.Label(root, text="", font=("Arial", 36), bg="#D3D3D3")
palavra_label.pack(pady=20)

chances_label = tk.Label(root, text="Chances restantes: ", font=("Arial", 18), bg="#D3D3D3")
chances_label.pack(pady=10)

letras_erradas_label = tk.Label(root, text="Letras erradas: ", font=("Arial", 18), bg="#D3D3D3")
letras_erradas_label.pack(pady=10)

entrada_letra = tk.Entry(root, font=("Arial", 24), width=5)
entrada_letra.pack(pady=20)

tentar_button = tk.Button(root, text="Tentar", font=("Arial", 18), command=tentar_letra)
tentar_button.pack(pady=20)

resultado_label = tk.Label(root, text="", font=("Arial", 15), bg="#D3D3D3")
resultado_label.pack(pady=30)

# Botão "Iniciar Jogo" com fundo azul claro
iniciar_button = tk.Button(root, text="Mudar Tema", font=("Arial", 18), command=iniciar_jogo, bg="#59e163")
iniciar_button.pack(pady=20)

# Iniciar o jogo ao carregar a interface
iniciar_jogo()

# Iniciar o loop do Tkinter
root.mainloop()
