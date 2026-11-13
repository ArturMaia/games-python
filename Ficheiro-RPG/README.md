# Gerador de Fichas de Personagem – D&D 5e

Aplicativo de desktop em Python (Tkinter) que gera fichas completas de personagens de Dungeons & Dragons 5ª Edição, em português. Ele calcula atributos, perícias, pontos de vida, CA e conjuração automaticamente, e inclui um rolador de dados e um sistema de descontos (regra caseira).

## O que o programa faz

- **Criação de personagem**: 9 raças, 12 classes, 12 antecedentes e níveis de 1 a 20.
- **Atributos**: gerados por 4d6 (descartando o menor), 3d6 clássico ou array padrão, distribuídos de forma otimizada para a classe ou aleatória.
- **Cálculos automáticos**: modificadores, bônus de proficiência, salvaguardas, perícias, PV, Classe de Armadura, iniciativa, deslocamento e bônus de ataque.
- **Conjuração**: CD, ataque mágico, espaços de magia e quantidade de truques e magias.
- **Rolador de dados**: aceita expressões como `2d6+3`, com vantagem ou desvantagem, e permite rolar testes direto da ficha.
- **Exportação**: imprime a ficha, salva em HTML ou TXT, ou copia o texto.

## Sistema de descontos

Regra caseira opcional, na aba **Descontos**:

1. O programa sorteia 2 ou 3 desvantagens, que dão pontos.
2. Com esses pontos, o jogador escolhe até 3 vantagens.
3. O gasto não pode ultrapassar os pontos ganhos.

Os efeitos entram na ficha automaticamente (por exemplo, -1 em um atributo ou +1 PV por nível). Os limites podem ser alterados no código, nas constantes `DESV_MIN`, `DESV_MAX` e `MAX_VANTAGENS`.

## Requisitos

- Python 3.8 ou superior
- Tkinter (já incluso no Python para Windows e macOS; no Linux, instale com `sudo apt install python3-tk`)

Não há outras dependências.

## Como usar

```bash
python gerador_ficha.py
```

1. Na aba **Criação**, preencha os dados do personagem e escolha as opções de geração.
2. (Opcional) Na aba **Descontos**, sorteie as desvantagens e escolha as vantagens.
3. Clique em **Gerar Personagem**. A ficha aparece na aba **Ficha**.
4. Use os botões da ficha para imprimir, salvar ou copiar.
5. Na aba **Dados**, role dados livremente ou faça testes com os valores da ficha.

## Limitações

- A ficha mostra as características de classe do nível 1; para os níveis seguintes, consulte o Livro do Jogador.
- Subclasses, talentos e magias específicas não são escolhidos pelo programa.
- O equipamento é o kit inicial padrão da classe.

---

Dungeons & Dragons é marca registrada da Wizards of the Coast. Este é um projeto não oficial.
