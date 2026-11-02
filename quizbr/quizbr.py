import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random

# Lista de perguntas
perguntas = [
    ["Qual o nome do primeiro presidente negro do Brasil?", "Afonso Pena", "Enéas Carneiro", "Nilo Peçanha", "Joaquim Barbosa", 3],
    ["Qual a primeira capital do Brasil?", "Salvador", "Rio de Janeiro", "Minas Gerais", "Brasília", 1],
    ["Quem é o autor(a) da canção O SEGUNDO SOL?", "Cazuza", "Cássia Eller", "Nando Reis", "Ney Matogrosso", 3],
    ["Qual dessas músicas não é de Jorge Ben Jor?","Carol,Carolina bela","Bete balanço","Magnólia","Domingas",2],
    ["Apelido de Edson Arantes do Nascimento:","Garrincha","Pelé","Cafú","Zico",2],
    ["Quem é o autor do livro CAPITÃES DE AREIA?", "Graciliano Ramos", "Clarice Lispector", "Ariano Suassuna", "Jorge Amado", 4],
    ["Em qual estado fica a estátua do Cristo redentor?","São Paulo","Distrito Federal","Espírito Santo","Rio de Janeiro",4],
    ["Qual o nome da mulher conhecida como a mãe do Samba?", "Leci Brandão", "Tia Ciata", "Dona Onete", "Alcione", 2],
    ["Qual o nome do pai da aviação?","Irmãos Wright","Bartolomeu Gusmão","Santos Dumont","Neil deGrasse Tyson",3],
    ["Qual a linguagem de programação não foi criada no Brasil?", "Egua", "Julia", "Portugol", "Lua", 2],
    ["Qual o nome da pioneira do modernismo brasileiro?", "Beatriz Nascimento", "Tarsila do Amaral", "Djamila Ribeiro", "Maria Auxiliadora", 2],
    ["Qual dessas não é uma comida típica do Brasil?","Feijoada","Maniçoba","Sushi","Tacacá",3],
    ["Qual o ano da abolição da escravidão?", "1888", "1822", "1695", "1500", 1],
    ["De quem é a música PAÍS TROPICAL?", "Cassiano", "Paulo Diniz", "Luís Melodia", "Jorge Ben", 4],
    ["De qual personagem é o bordão E O SALÁRIO, Ó?", "Mussum", "Grande Otelo", "Caco Antibes", "Professor Raimundo", 4],
    ["De quem é a música MEDO DA CHUVA?","Djavan","Tim Maia","Raul Seixas","Gilberto Gil",3],
    ["Cidade mais populosa do Brasil:","São Paulo","Brasília","Porto Alegre","João Pessoa",1],
    ["Ano em que o Brasil foi pentacampeão mundial de futebol:","2002","1989","2000","1995",1],
    ["Qual desses estados não faz da região norte do Brasil?","Roraima","Rondônia","Maranhão","Tocantins",3],
    ["Cartunista criador do personagem MENINO MALUQUINHO:","Mauricio de Souza","Henfil","Laerte","Ziraldo",4],
    ["Qual foi o período da ditadura no Brasil?","1960-1975","1964-1985","1970-1980","1974-1989",2],
    ["Prato típico é cozido por 7 dias por ser feito com folhas venenosas?","Tacacá","Caruru","Maniçoba","Chibé",3],
    ["Qual presidente criou as cotas raciais?","Dilma Rousseff","Lula","Tancredo Neves","Michel Temer",1],
    ["Mané Galinha é um personagem de qual filme?","Central do Brasil","Cidade de Deus","Cidade dos homens","Era uma vez",2],
    ["Quem criou o CLT no Brasil?","Lula","Jair Bolsonaro","Fernando Collor","Getúlio Vargas",4],
    ["Qual desses não é o nome de uma facção no Brasil?","Facção Central","Primeiro Comando da Capital (PCC)","Comando Vermelho","Amigos dos Amigos",1],
    ["De quem é a música MALANDRAGEM?","Rita Lee","Cássia Eller","Bezerra da Silva","Mart'nália",2],
    ["Agostinho e Tuco são personagem da série:","Toma Lá Dá Cá","Cine Holliúdy","Tapas e Beijos","A Grande Família",4],
    ["Qual dessas coisas não foi inventada por brasileiros:","Coração artificial","Rádio","Relógio de pulso","Carro",4],
    ["Qual o nome da primeira atriz negra do Brasil?","Enedina Alves Marques","Sonia Guimarães","Ruth de Souza","Maria Odília Teixeira",3],
    ["Qual o nome do maior abolicionista (patrono da abolição da escravidão no país) do Brasil?","Luís Gama","André Rebouças","Juliano Moreira","Lazáro Ramos",1]
    ]

# Embaralha as perguntas para exibi-las em ordem aleatória
random.shuffle(perguntas)

# Limitar a 10 perguntas
perguntas = perguntas[:10]

# Criar DataFrame do pandas
df = pd.DataFrame(perguntas, columns=["Pergunta", "Opção 1", "Opção 2", "Opção 3", "Opção 4", "Resposta"])

score = 0  # Inicia a pontuação do jogador
current_question = 0  # Questão atual

# Função para exibir uma nova pergunta
def exibir_pergunta():
    global current_question

    # Se todas as perguntas foram respondidas, exibe o resultado final
    if current_question >= len(df):
        mostrar_resultado()
        return
    
    pergunta = df.iloc[current_question]  # Pergunta atual
    pergunta_texto = pergunta['Pergunta']
    opcoes = [pergunta['Opção 1'], pergunta['Opção 2'], pergunta['Opção 3'], pergunta['Opção 4']]

    # Atualiza o texto da pergunta e as opções
    label_pergunta.config(text=pergunta_texto)
    botoes_opcoes[0].config(text=opcoes[0], bg="yellow")
    botoes_opcoes[1].config(text=opcoes[1], bg="yellow")
    botoes_opcoes[2].config(text=opcoes[2], bg="yellow")
    botoes_opcoes[3].config(text=opcoes[3], bg="yellow")

    # Resetar as cores dos botões
    for botao in botoes_opcoes:
        botao.config(state="normal", bg="yellow")

# Função para verificar a resposta do usuário
def verificar_resposta(opcao_escolhida):
    global score, current_question

    resposta_correta = df.iloc[current_question]['Resposta']
    
    # Verifica se a resposta do usuário está correta
    if opcao_escolhida == resposta_correta:
        score += 1  # Aumenta a pontuação
        botoes_opcoes[opcao_escolhida - 1].config(bg="#00cb6a")  # Resposta certa fica verde
        messagebox.showinfo("Resposta Correta", "Você acertou a pergunta!")
    else:
        botoes_opcoes[opcao_escolhida - 1].config(bg="#ec2552")  # Resposta errada fica vermelha
        botoes_opcoes[resposta_correta - 1].config(bg="#00cb6a")  # Destaca a resposta correta
        messagebox.showinfo("Resposta Errada", "Você errou a pergunta.")

    # Desabilita os botões após a resposta
    for botao in botoes_opcoes:
        botao.config(state="disabled")
    
    # Passa para a próxima pergunta
    current_question += 1
    root.after(1000, exibir_pergunta)  # Atraso de 1 segundo para mostrar a próxima pergunta

# Função para mostrar o resultado final
def mostrar_resultado():
    messagebox.showinfo("Resultado", f"Você acertou {score} de 10 perguntas!")
    root.quit()  # Fecha a aplicação

# Criação da interface gráfica
root = tk.Tk()
root.title("Quiz do Conhecimento")

# Tamanho da janela
root.geometry("400x400")

# Label para exibir a pergunta
label_pergunta = tk.Label(root, text="", font=("Arial", 14), wraplength=350, justify="center")
label_pergunta.pack(pady=20)

# Botões para as opções de resposta
botoes_opcoes = []
for i in range(4):
    botao = tk.Button(
        root, text="", 
        font=("Arial", 12, "bold"),  # Texto em negrito
        width=30, 
        height=2,  # Tamanho dos botões
        bg="yellow",  # Cor de fundo amarelo
        fg="black",   # Cor da fonte preta
        activebackground="gold",  # Cor de fundo quando o botão é pressionado
        command=lambda i=i: verificar_resposta(i+1)  # Passa a opção como argumento
    )
    botao.pack(pady=5)
    botoes_opcoes.append(botao)

# Usando o método after para exibir a primeira pergunta após a interface carregar
root.after(100, exibir_pergunta)  # 100ms de atraso para garantir que a interface seja carregada

# Iniciar o loop da interface gráfica
root.mainloop()
