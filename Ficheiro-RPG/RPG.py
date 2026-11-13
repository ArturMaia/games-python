# -*- coding: utf-8 -*-
"""
Gerador de Fichas de Personagem - D&D 5ª Edição
------------------------------------------------
Recursos:
  * Raças, classes e antecedentes da 5e (SRD)
  * Atributos por 4d6 (descarta o menor), 3d6 clássico ou array padrão
  * Bônus raciais, modificadores, proficiência, PV, CA, salvaguardas, perícias
  * Conjuração (CD, ataque, espaços de magia, truques, magias)
  * Níveis 1 a 20 (aumentos de atributo automáticos)
  * Rolador de dados (expressões como 2d6+3, vantagem/desvantagem, testes da ficha)
  * Sistema de descontos: 2 ou 3 desvantagens sorteadas dão pontos; o jogador
    escolhe até 3 vantagens com esses pontos
  * Imprimir ficha (abre no navegador já com a janela de impressão),
    salvar em HTML ou TXT
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import random
import re
import os
import html
import tempfile
import webbrowser

MARROM = "#8B4513"

# ----------------------------------------------------------------------------
# DADOS DO JOGO
# ----------------------------------------------------------------------------
ATRIBUTOS = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
NOMES_ATRIBUTOS = {
    "FOR": "Força", "DES": "Destreza", "CON": "Constituição",
    "INT": "Inteligência", "SAB": "Sabedoria", "CAR": "Carisma",
}

PERICIAS = {
    "Acrobacia": "DES", "Adestrar Animais": "SAB", "Arcanismo": "INT",
    "Atletismo": "FOR", "Atuação": "CAR", "Enganação": "CAR",
    "Furtividade": "DES", "História": "INT", "Intimidação": "CAR",
    "Intuição": "SAB", "Investigação": "INT", "Medicina": "SAB",
    "Natureza": "INT", "Percepção": "SAB", "Persuasão": "CAR",
    "Prestidigitação": "DES", "Religião": "INT", "Sobrevivência": "SAB",
}

ALINHAMENTOS = [
    "Leal e Bom", "Neutro e Bom", "Caótico e Bom",
    "Leal e Neutro", "Neutro", "Caótico e Neutro",
    "Leal e Mau", "Neutro e Mau", "Caótico e Mau",
]

RACAS = {
    "Humano": {
        "bonus": {a: 1 for a in ATRIBUTOS}, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "+1 idioma à escolha"],
        "tracos": ["Versátil: +1 em todos os atributos"],
    },
    "Anão": {
        "bonus": {"CON": 2}, "deslocamento": 7.5, "tamanho": "Médio",
        "idiomas": ["Comum", "Anão"],
        "tracos": ["Visão no Escuro (18 m)",
                   "Resiliência Anã (vantagem contra veneno e resistência a dano de veneno)",
                   "Treinamento em Combate Anão (machados e martelos)",
                   "Especialização em Pedra"],
    },
    "Elfo": {
        "bonus": {"DES": 2}, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "Élfico"], "pericias": ["Percepção"],
        "tracos": ["Visão no Escuro (18 m)", "Sentidos Aguçados (proficiência em Percepção)",
                   "Ancestral Feérico (vantagem contra encantamento)",
                   "Transe (4 horas de meditação em vez de dormir)"],
    },
    "Halfling": {
        "bonus": {"DES": 2}, "deslocamento": 7.5, "tamanho": "Pequeno",
        "idiomas": ["Comum", "Halfling"],
        "tracos": ["Sortudo (re-rola 1 natural em d20)",
                   "Corajoso (vantagem contra amedrontado)",
                   "Agilidade Halfling (passa por criaturas maiores)"],
    },
    "Draconato": {
        "bonus": {"FOR": 2, "CAR": 1}, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "Dracônico"],
        "tracos": ["Ancestralidade Dracônica", "Arma de Sopro",
                   "Resistência a Dano (conforme o dragão ancestral)"],
    },
    "Gnomo": {
        "bonus": {"INT": 2}, "deslocamento": 7.5, "tamanho": "Pequeno",
        "idiomas": ["Comum", "Gnômico"],
        "tracos": ["Visão no Escuro (18 m)",
                   "Esperteza Gnômica (vantagem em salvaguardas de INT, SAB e CAR contra magia)"],
    },
    "Meio-Elfo": {
        "bonus": {"CAR": 2}, "extra": 2, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "Élfico", "+1 idioma à escolha"], "pericias_livres": 2,
        "tracos": ["+1 em dois outros atributos", "Visão no Escuro (18 m)",
                   "Ancestral Feérico", "Versatilidade em Perícias (2 perícias extras)"],
    },
    "Meio-Orc": {
        "bonus": {"FOR": 2, "CON": 1}, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "Orc"], "pericias": ["Intimidação"],
        "tracos": ["Visão no Escuro (18 m)", "Ameaçador (proficiência em Intimidação)",
                   "Resistência Implacável (cai a 1 PV em vez de 0, 1x por descanso longo)",
                   "Ataques Selvagens (dado extra em crítico corpo a corpo)"],
    },
    "Tiefling": {
        "bonus": {"CAR": 2, "INT": 1}, "deslocamento": 9, "tamanho": "Médio",
        "idiomas": ["Comum", "Infernal"],
        "tracos": ["Visão no Escuro (18 m)", "Resistência Infernal (resistência a fogo)",
                   "Legado Infernal (Taumaturgia; magias extras em níveis mais altos)"],
    },
}

ANTECEDENTES = {
    "Acólito": (["Intuição", "Religião"], "Abrigo dos Fiéis"),
    "Criminoso": (["Enganação", "Furtividade"], "Contato Criminoso"),
    "Artesão da Guilda": (["Intuição", "Persuasão"], "Membro da Guilda"),
    "Eremita": (["Medicina", "Religião"], "Descoberta"),
    "Forasteiro": (["Atletismo", "Sobrevivência"], "Andarilho"),
    "Nobre": (["História", "Persuasão"], "Posição de Privilégio"),
    "Sábio": (["Arcanismo", "História"], "Pesquisador"),
    "Soldado": (["Atletismo", "Intimidação"], "Patente Militar"),
    "Charlatão": (["Enganação", "Prestidigitação"], "Identidade Falsa"),
    "Artista": (["Acrobacia", "Atuação"], "Pelo Povo"),
    "Herói do Povo": (["Adestrar Animais", "Sobrevivência"], "Hospitalidade Rústica"),
    "Marinheiro": (["Atletismo", "Percepção"], "Passagem de Navio"),
}

TODAS_PERICIAS = list(PERICIAS.keys())

CLASSES = {
    "Bárbaro": {
        "dado": 12, "salvaguardas": ["FOR", "CON"], "n_pericias": 2,
        "pericias": ["Adestrar Animais", "Atletismo", "Intimidação", "Natureza", "Percepção", "Sobrevivência"],
        "prioridade": ["FOR", "CON", "DES", "SAB", "CAR", "INT"],
        "profs": "Armaduras leves e médias, escudos; armas simples e marciais",
        "tracos": ["Fúria (bônus de dano, resistência a dano físico; 2 usos)",
                   "Defesa sem Armadura (CA = 10 + DES + CON)"],
        "equip": ["Machado grande (ou arma marcial)", "2 machados de mão", "Pacote de aventureiro", "4 azagaias"],
        "ca": (lambda m: 10 + m["DES"] + m["CON"], "Defesa sem Armadura (10 + DES + CON)"),
        "conj": None,
    },
    "Bardo": {
        "dado": 8, "salvaguardas": ["DES", "CAR"], "n_pericias": 3, "pericias": TODAS_PERICIAS,
        "prioridade": ["CAR", "DES", "CON", "SAB", "INT", "FOR"],
        "profs": "Armaduras leves; armas simples, bestas de mão, espadas longas, rapieiras, espadas curtas; 3 instrumentos musicais",
        "tracos": ["Inspiração de Bardo (d6; usos = mod. CAR)", "Conjuração"],
        "equip": ["Rapieira", "Pacote de artista", "Alaúde (ou outro instrumento)", "Armadura de couro", "Adaga"],
        "ca": (lambda m: 11 + m["DES"], "Armadura de couro (11 + DES)"),
        "conj": "cheio", "hab_conj": "CAR",
    },
    "Bruxo": {
        "dado": 8, "salvaguardas": ["SAB", "CAR"], "n_pericias": 2,
        "pericias": ["Arcanismo", "Enganação", "História", "Intimidação", "Investigação", "Natureza", "Religião"],
        "prioridade": ["CAR", "CON", "DES", "SAB", "INT", "FOR"],
        "profs": "Armaduras leves; armas simples",
        "tracos": ["Patrono Transcendental", "Magia de Pacto"],
        "equip": ["Besta leve e 20 virotes", "Foco arcano", "Pacote de estudioso", "Armadura de couro", "2 adagas"],
        "ca": (lambda m: 11 + m["DES"], "Armadura de couro (11 + DES)"),
        "conj": "pacto", "hab_conj": "CAR",
    },
    "Clérigo": {
        "dado": 8, "salvaguardas": ["SAB", "CAR"], "n_pericias": 2,
        "pericias": ["História", "Intuição", "Medicina", "Persuasão", "Religião"],
        "prioridade": ["SAB", "CON", "FOR", "DES", "CAR", "INT"],
        "profs": "Armaduras leves e médias, escudos; armas simples",
        "tracos": ["Domínio Divino (escolha no nível 1)", "Conjuração"],
        "equip": ["Maça", "Cota de escamas", "Escudo", "Símbolo sagrado", "Pacote de sacerdote", "Besta leve e 20 virotes"],
        "ca": (lambda m: 14 + min(m["DES"], 2) + 2, "Cota de escamas + escudo (14 + DES máx. 2 + 2)"),
        "conj": "cheio", "hab_conj": "SAB",
    },
    "Druida": {
        "dado": 8, "salvaguardas": ["INT", "SAB"], "n_pericias": 2,
        "pericias": ["Arcanismo", "Adestrar Animais", "Intuição", "Medicina", "Natureza", "Percepção", "Religião", "Sobrevivência"],
        "prioridade": ["SAB", "CON", "DES", "INT", "CAR", "FOR"],
        "profs": "Armaduras leves e médias não metálicas, escudos; clavas, adagas, dardos, azagaias, maças, bordões, cimitarras, foices, fundas, lanças",
        "tracos": ["Druídico (idioma secreto)", "Conjuração"],
        "equip": ["Escudo de madeira", "Cimitarra", "Armadura de couro", "Pacote de aventureiro", "Foco druídico"],
        "ca": (lambda m: 11 + m["DES"] + 2, "Armadura de couro + escudo (11 + DES + 2)"),
        "conj": "cheio", "hab_conj": "SAB",
    },
    "Feiticeiro": {
        "dado": 6, "salvaguardas": ["CON", "CAR"], "n_pericias": 2,
        "pericias": ["Arcanismo", "Enganação", "Intuição", "Intimidação", "Persuasão", "Religião"],
        "prioridade": ["CAR", "CON", "DES", "SAB", "INT", "FOR"],
        "profs": "Adagas, dardos, fundas, bordões, bestas leves",
        "tracos": ["Origem de Feitiçaria (escolha no nível 1)", "Conjuração"],
        "equip": ["Besta leve e 20 virotes", "Foco arcano", "Pacote de explorador", "2 adagas"],
        "ca": (lambda m: 10 + m["DES"], "Sem armadura (10 + DES)"),
        "conj": "cheio", "hab_conj": "CAR",
    },
    "Guerreiro": {
        "dado": 10, "salvaguardas": ["FOR", "CON"], "n_pericias": 2,
        "pericias": ["Acrobacia", "Adestrar Animais", "Atletismo", "História", "Intuição", "Intimidação", "Percepção", "Sobrevivência"],
        "prioridade": ["FOR", "CON", "DES", "SAB", "CAR", "INT"],
        "profs": "Todas as armaduras, escudos; armas simples e marciais",
        "tracos": ["Estilo de Luta", "Retomar o Fôlego (1d10 + nível de PV, 1x por descanso)"],
        "equip": ["Cota de malha", "Espada longa e escudo", "Besta leve e 20 virotes", "Pacote de aventureiro"],
        "ca": (lambda m: 16 + 2, "Cota de malha + escudo (16 + 2)"),
        "conj": None,
    },
    "Ladino": {
        "dado": 8, "salvaguardas": ["DES", "INT"], "n_pericias": 4,
        "pericias": ["Acrobacia", "Atletismo", "Atuação", "Enganação", "Furtividade", "Intimidação",
                     "Intuição", "Investigação", "Percepção", "Persuasão", "Prestidigitação"],
        "prioridade": ["DES", "INT", "CON", "CAR", "SAB", "FOR"],
        "profs": "Armaduras leves; armas simples, bestas de mão, espadas longas, rapieiras, espadas curtas; ferramentas de ladrão",
        "tracos": ["Especialização (2 perícias com proficiência dobrada)", "Ataque Furtivo",
                   "Gíria de Ladrão"],
        "equip": ["Rapieira", "Arco curto e 20 flechas", "Armadura de couro", "2 adagas", "Ferramentas de ladrão", "Pacote de assaltante"],
        "ca": (lambda m: 11 + m["DES"], "Armadura de couro (11 + DES)"),
        "conj": None,
    },
    "Mago": {
        "dado": 6, "salvaguardas": ["INT", "SAB"], "n_pericias": 2,
        "pericias": ["Arcanismo", "História", "Intuição", "Investigação", "Medicina", "Religião"],
        "prioridade": ["INT", "CON", "DES", "SAB", "CAR", "FOR"],
        "profs": "Adagas, dardos, fundas, bordões, bestas leves",
        "tracos": ["Conjuração (grimório)", "Recuperação Arcana"],
        "equip": ["Bordão", "Bolsa de componentes", "Grimório", "Pacote de estudioso"],
        "ca": (lambda m: 10 + m["DES"], "Sem armadura (10 + DES; Armadura Arcana = 13 + DES)"),
        "conj": "cheio", "hab_conj": "INT",
    },
    "Monge": {
        "dado": 8, "salvaguardas": ["FOR", "DES"], "n_pericias": 2,
        "pericias": ["Acrobacia", "Atletismo", "História", "Intuição", "Religião", "Furtividade"],
        "prioridade": ["DES", "SAB", "CON", "FOR", "INT", "CAR"],
        "profs": "Armas simples e espadas curtas",
        "tracos": ["Defesa sem Armadura (CA = 10 + DES + SAB)", "Artes Marciais"],
        "equip": ["Espada curta", "10 dardos", "Pacote de explorador"],
        "ca": (lambda m: 10 + m["DES"] + m["SAB"], "Defesa sem Armadura (10 + DES + SAB)"),
        "conj": None,
    },
    "Paladino": {
        "dado": 10, "salvaguardas": ["SAB", "CAR"], "n_pericias": 2,
        "pericias": ["Atletismo", "Intuição", "Intimidação", "Medicina", "Persuasão", "Religião"],
        "prioridade": ["FOR", "CAR", "CON", "SAB", "DES", "INT"],
        "profs": "Todas as armaduras, escudos; armas simples e marciais",
        "tracos": ["Sentido Divino", "Mãos Consagradas (reserva de 5 x nível PV)"],
        "equip": ["Espada longa e escudo", "5 azagaias", "Cota de malha", "Símbolo sagrado", "Pacote de sacerdote"],
        "ca": (lambda m: 16 + 2, "Cota de malha + escudo (16 + 2)"),
        "conj": "meio", "hab_conj": "CAR",
    },
    "Patrulheiro": {
        "dado": 10, "salvaguardas": ["FOR", "DES"], "n_pericias": 3,
        "pericias": ["Adestrar Animais", "Atletismo", "Intuição", "Investigação", "Natureza", "Percepção", "Furtividade", "Sobrevivência"],
        "prioridade": ["DES", "SAB", "CON", "FOR", "INT", "CAR"],
        "profs": "Armaduras leves e médias, escudos; armas simples e marciais",
        "tracos": ["Inimigo Favorito", "Explorador Nato"],
        "equip": ["Cota de escamas", "2 espadas curtas", "Arco longo e 20 flechas", "Pacote de explorador"],
        "ca": (lambda m: 14 + min(m["DES"], 2), "Cota de escamas (14 + DES máx. 2)"),
        "conj": "meio", "hab_conj": "SAB",
    },
}

# Nível em que cada classe escolhe sua subclasse
NIVEL_SUBCLASSE = {
    "Clérigo": 1, "Feiticeiro": 1, "Bruxo": 1, "Druida": 2, "Mago": 2,
}
CLASSES_ATAQUE_EXTRA = ["Bárbaro", "Guerreiro", "Monge", "Paladino", "Patrulheiro"]

# Espaços de magia por nível (índice 0 = nível 1 do personagem)
SLOTS_CHEIO = [
    [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2],
    [4, 3, 3, 3, 1], [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1],
    [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1],
]
SLOTS_MEIO = [
    [], [2], [3], [3], [4, 2], [4, 2], [4, 3], [4, 3], [4, 3, 2], [4, 3, 2],
    [4, 3, 3], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 1], [4, 3, 3, 2], [4, 3, 3, 2],
    [4, 3, 3, 3, 1], [4, 3, 3, 3, 1], [4, 3, 3, 3, 2], [4, 3, 3, 3, 2],
]
# Bruxo: (quantidade, nível do espaço)
SLOTS_PACTO = [
    (1, 1), (2, 1), (2, 2), (2, 2), (2, 3), (2, 3), (2, 4), (2, 4), (2, 5), (2, 5),
    (3, 5), (3, 5), (3, 5), (3, 5), (3, 5), (3, 5), (4, 5), (4, 5), (4, 5), (4, 5),
]
TRUQUES = {
    "Bardo": (2, 3, 4), "Bruxo": (2, 3, 4), "Clérigo": (3, 4, 5),
    "Druida": (2, 3, 4), "Feiticeiro": (4, 5, 6), "Mago": (3, 4, 5),
}
MAGIAS_CONHECIDAS = {
    "Bardo": [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 15, 16, 18, 19, 19, 20, 22, 22, 22],
    "Feiticeiro": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
    "Bruxo": [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15],
    "Patrulheiro": [0, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11],
}


# ----------------------------------------------------------------------------
# SISTEMA DE DESCONTOS (homebrew)
#   As desvantagens são SORTEADAS (entre DESV_MIN e DESV_MAX) e dão pontos.
#   O jogador ESCOLHE até MAX_VANTAGENS vantagens, gastando esses pontos.
#   Os pontos gastos não podem passar dos pontos ganhos.
# ----------------------------------------------------------------------------
DESV_MIN = 2          # mínimo de desvantagens sorteadas
DESV_MAX = 3          # máximo de desvantagens sorteadas
MAX_VANTAGENS = 3     # máximo de vantagens que o jogador pode comprar

DESVANTAGENS = {
    "Vício": {"pts": 1, "desc": "Tem um vício e precisa satisfazê-lo todo dia; sem isso, desvantagem em salvaguardas de SAB (defina o vício com o mestre).", "efeito": {}},
    "Fobia": {"pts": 1, "desc": "Medo irracional: desvantagem em testes e ataques enquanto o gatilho estiver à vista (defina o gatilho com o mestre).", "efeito": {}},
    "Inimigo poderoso": {"pts": 2, "desc": "Alguém influente quer o personagem arruinado; o mestre pode usá-lo na história.", "efeito": {}},
    "Procurado pela lei": {"pts": 2, "desc": "Há recompensa pela cabeça do personagem em ao menos uma região.", "efeito": {}},
    "Dívida pesada": {"pts": 1, "desc": "Deve muito a alguém perigoso; haverá cobranças periódicas.", "efeito": {}},
    "Maldição leve": {"pts": 2, "desc": "Uma maldição menor (definida com o mestre) atrapalha em momentos dramáticos.", "efeito": {}},
    "Código de honra rígido": {"pts": 1, "desc": "Nunca mente, nunca ataca desarmados, nunca abandona um desafio.", "efeito": {}},
    "Ferimento antigo": {"pts": 2, "desc": "Deslocamento -1,5 m e -1 PV por nível.", "efeito": {"desl": -1.5, "pv_nivel": -1}},
    "Fraqueza física": {"pts": 2, "desc": "-1 em FOR, DES ou CON (sorteado).", "efeito": {"penal_fisica": 1}},
    "Mente frágil": {"pts": 2, "desc": "-1 em INT, SAB ou CAR (sorteado).", "efeito": {"penal_mental": 1}},
    "Visão fraca": {"pts": 2, "desc": "Percepção passiva -2 e desvantagem em Percepção visual à distância.", "efeito": {"passiva": -2}},
    "Reflexos lentos": {"pts": 1, "desc": "-2 na iniciativa.", "efeito": {"iniciativa": -2}},
    "Alergia grave": {"pts": 1, "desc": "Uma substância comum causa reações graves (definida com o mestre).", "efeito": {}},
    "Analfabeto": {"pts": 1, "desc": "Não sabe ler nem escrever.", "efeito": {}},
    "Pobre": {"pts": 1, "desc": "Começa sem moedas e apenas com o básico.", "efeito": {}},
}

VANTAGENS = {
    "+1 no atributo principal": {"custo": 2, "desc": "+1 no atributo mais importante da classe (máx. 20).", "efeito": {"atrib_idx": 0}},
    "+1 no segundo atributo": {"custo": 2, "desc": "+1 no segundo atributo da classe (máx. 20).", "efeito": {"atrib_idx": 1}},
    "Perícia extra": {"custo": 1, "desc": "Proficiência em uma perícia adicional.", "efeito": {"pericia_extra": 1}},
    "Especialização numa perícia": {"custo": 2, "desc": "Dobra a proficiência em uma perícia já treinada.", "efeito": {"expertise": 1}},
    "Salvaguarda extra": {"custo": 2, "desc": "Proficiência em uma salvaguarda adicional.", "efeito": {"save_extra": 1}},
    "+1 PV por nível": {"custo": 2, "desc": "Um ponto de vida extra a cada nível.", "efeito": {"pv_nivel": 1}},
    "Pés ligeiros": {"custo": 1, "desc": "+3 m de deslocamento.", "efeito": {"desl": 3}},
    "Reflexos rápidos": {"custo": 1, "desc": "+2 na iniciativa.", "efeito": {"iniciativa": 2}},
    "Treino defensivo": {"custo": 3, "desc": "+1 na Classe de Armadura.", "efeito": {"ca": 1}},
    "Talento inicial": {"custo": 3, "desc": "Um talento à escolha (consulte o Livro do Jogador).", "efeito": {"talento": 1}},
    "Idioma extra": {"custo": 1, "desc": "Aprende um idioma adicional.", "efeito": {"idioma": 1}},
    "Inspiração inicial": {"custo": 1, "desc": "Começa a aventura com Inspiração.", "efeito": {"inspiracao": 1}},
    "Item mágico comum": {"custo": 2, "desc": "Um item mágico comum, definido com o mestre.", "efeito": {"item": 1}},
    "Bolsa extra": {"custo": 1, "desc": "+100 po iniciais.", "efeito": {"po": 1}},
    "Resistência a um tipo de dano": {"custo": 4, "desc": "Resistência a um tipo de dano (escolhido com o mestre).", "efeito": {"resistencia": 1}},
    "Aliado ou mentor": {"custo": 1, "desc": "Um NPC aliado que pode ajudar na campanha.", "efeito": {}},
}


# ----------------------------------------------------------------------------
# REGRAS / GERAÇÃO
# ----------------------------------------------------------------------------
def sg(n):
    """Formata número com sinal (+3, -1)."""
    return f"{n:+d}"


def modificador(valor):
    return (valor - 10) // 2


def rolar_4d6():
    dados = sorted(random.randint(1, 6) for _ in range(4))
    return sum(dados[1:]), dados


def rolar_3d6():
    dados = [random.randint(1, 6) for _ in range(3)]
    return sum(dados), dados


def bonus_proficiencia(nivel):
    return 2 + (nivel - 1) // 4


def niveis_aumento_atributo(classe, nivel):
    niveis = [4, 8, 12, 16, 19]
    if classe == "Guerreiro":
        niveis += [6, 14]
    if classe == "Ladino":
        niveis += [10]
    return [n for n in niveis if n <= nivel]


def info_magia(classe_nome, nivel, mods, prof):
    c = CLASSES[classe_nome]
    tipo = c["conj"]
    if not tipo or (tipo == "meio" and nivel < 2):
        return None
    hab = c["hab_conj"]
    mod = mods[hab]
    info = {"habilidade": hab, "cd": 8 + prof + mod, "ataque": prof + mod,
            "slots": [], "truques": 0, "magias": ""}

    if tipo == "cheio":
        info["slots"] = [(i + 1, q) for i, q in enumerate(SLOTS_CHEIO[nivel - 1])]
    elif tipo == "meio":
        info["slots"] = [(i + 1, q) for i, q in enumerate(SLOTS_MEIO[nivel - 1])]
    else:
        qtd, circ = SLOTS_PACTO[nivel - 1]
        info["slots"] = [(circ, qtd)]
        info["pacto"] = True

    if classe_nome in TRUQUES:
        t = TRUQUES[classe_nome]
        info["truques"] = t[2] if nivel >= 10 else t[1] if nivel >= 4 else t[0]

    if classe_nome in ("Clérigo", "Druida", "Mago"):
        n = max(1, mod + nivel)
        info["magias"] = f"{n} magias preparadas" + (" (do grimório)" if classe_nome == "Mago" else "")
    elif classe_nome == "Paladino":
        info["magias"] = f"{max(1, mod + nivel // 2)} magias preparadas"
    else:
        info["magias"] = f"{MAGIAS_CONHECIDAS[classe_nome][nivel - 1]} magias conhecidas"
    return info


def criar_personagem(d):
    """Recebe o dicionário do formulário e devolve a ficha completa."""
    classe = CLASSES[d["classe"]]
    raca = RACAS[d["raca"]]
    pericias_ante, traco_ante = ANTECEDENTES[d["antecedente"]]
    nivel = d["nivel"]
    desvs = list(d.get("desv_sel", []))
    vants = list(d.get("vant_sel", []))
    log = []
    notas = []

    def somar(chave):
        total = 0
        for n in desvs:
            total += DESVANTAGENS[n]["efeito"].get(chave, 0)
        for n in vants:
            total += VANTAGENS[n]["efeito"].get(chave, 0)
        return total

    # 1) Geração dos valores
    metodo = d["metodo"]
    if metodo == "Array padrão (15,14,13,12,10,8)":
        valores = [15, 14, 13, 12, 10, 8]
        log.append("Array padrão: 15, 14, 13, 12, 10, 8")
    elif metodo == "3d6 clássico":
        valores = []
        for _ in range(6):
            total, dados = rolar_3d6()
            valores.append(total)
            log.append(f"3d6: {dados} = {total}")
    else:
        valores = []
        for _ in range(6):
            total, dados = rolar_4d6()
            valores.append(total)
            log.append(f"4d6: {dados} (descarta {dados[0]}) = {total}")

    # 2) Distribuição
    if d["distribuicao"] == "Otimizada para a classe":
        ordenados = sorted(valores, reverse=True)
        base = dict(zip(classe["prioridade"], ordenados))
    else:
        embaralhados = valores[:]
        random.shuffle(embaralhados)
        base = dict(zip(ATRIBUTOS, embaralhados))

    # 3) Bônus raciais
    bonus = dict(raca["bonus"])
    if raca.get("extra"):
        candidatos = [a for a in ATRIBUTOS if a not in bonus]
        for a in random.sample(candidatos, raca["extra"]):
            bonus[a] = bonus.get(a, 0) + 1

    final = {a: base[a] + bonus.get(a, 0) for a in ATRIBUTOS}

    # 4) Aumentos de atributo por nível (+2 distribuídos pela prioridade da classe)
    aumentos = niveis_aumento_atributo(d["classe"], nivel)
    for _ in aumentos:
        pontos = 2
        for a in classe["prioridade"]:
            while pontos and final[a] < 20:
                final[a] += 1
                pontos -= 1
            if not pontos:
                break

    # 4b) Efeitos de descontos sobre atributos
    for n in desvs:
        ef = DESVANTAGENS[n]["efeito"]
        if ef.get("penal_fisica"):
            a = random.choice(["FOR", "DES", "CON"])
            final[a] = max(1, final[a] - 1)
            notas.append(f"{n}: -1 em {a}")
        if ef.get("penal_mental"):
            a = random.choice(["INT", "SAB", "CAR"])
            final[a] = max(1, final[a] - 1)
            notas.append(f"{n}: -1 em {a}")
    for n in vants:
        ef = VANTAGENS[n]["efeito"]
        if "atrib_idx" in ef:
            a = classe["prioridade"][ef["atrib_idx"]]
            final[a] = min(20, final[a] + 1)
            notas.append(f"{n}: +1 em {a}")

    mods = {a: modificador(final[a]) for a in ATRIBUTOS}
    prof = bonus_proficiencia(nivel)

    # 5) Perícias
    prof_pericias = set(pericias_ante) | set(raca.get("pericias", []))
    for _ in range(raca.get("pericias_livres", 0)):
        livres = [s for s in TODAS_PERICIAS if s not in prof_pericias]
        prof_pericias.add(random.choice(livres))
    pool = [s for s in classe["pericias"] if s not in prof_pericias]
    if len(pool) < classe["n_pericias"]:
        pool += [s for s in TODAS_PERICIAS if s not in prof_pericias and s not in pool]
    prof_pericias |= set(random.sample(pool, classe["n_pericias"]))

    for _ in range(somar("pericia_extra")):
        livres = [s for s in classe["pericias"] if s not in prof_pericias] or \
                 [s for s in TODAS_PERICIAS if s not in prof_pericias]
        if livres:
            s = random.choice(livres)
            prof_pericias.add(s)
            notas.append(f"Perícia extra: {s}")

    # Especialização (Ladino / Bardo)
    n_exp = 0
    if d["classe"] == "Ladino":
        n_exp = 4 if nivel >= 6 else 2
    elif d["classe"] == "Bardo":
        n_exp = 4 if nivel >= 10 else 2 if nivel >= 3 else 0
    especialistas = set(random.sample(sorted(prof_pericias), min(n_exp, len(prof_pericias))))
    for _ in range(somar("expertise")):
        cand = sorted(prof_pericias - especialistas)
        if cand:
            s = random.choice(cand)
            especialistas.add(s)
            notas.append(f"Especialização extra: {s}")

    pericias = {}
    for nome, attr in PERICIAS.items():
        p = nome in prof_pericias
        e = nome in especialistas
        val = mods[attr] + (prof * 2 if e else prof if p else 0)
        pericias[nome] = {"mod": val, "prof": p, "exp": e, "attr": attr}

    saves_prof = set(classe["salvaguardas"])
    for _ in range(somar("save_extra")):
        cand = [a for a in ATRIBUTOS if a not in saves_prof]
        if cand:
            a = random.choice(cand)
            saves_prof.add(a)
            notas.append(f"Salvaguarda extra: {NOMES_ATRIBUTOS[a]}")
    saves = {a: {"mod": mods[a] + (prof if a in saves_prof else 0),
                 "prof": a in saves_prof} for a in ATRIBUTOS}

    # 6) Pontos de vida
    dado = classe["dado"]
    pv = dado + mods["CON"]
    for _ in range(nivel - 1):
        ganho = random.randint(1, dado) if d["pv_metodo"] == "Rolar dado" else dado // 2 + 1
        pv += max(1, ganho + mods["CON"])
    pv = max(1, pv + somar("pv_nivel") * nivel)

    # 7) Classe de Armadura, deslocamento, iniciativa
    ca_val, ca_desc = classe["ca"][0](mods), classe["ca"][1]
    if somar("ca"):
        ca_val += somar("ca")
        ca_desc += f" +{somar('ca')} (Treino defensivo)"
    deslocamento = max(1.5, raca["deslocamento"] + somar("desl"))
    iniciativa = mods["DES"] + somar("iniciativa")
    passiva = 10 + pericias["Percepção"]["mod"] + somar("passiva")

    # 8) Características, idiomas e equipamento
    caract = list(classe["tracos"])
    sub = NIVEL_SUBCLASSE.get(d["classe"], 3)
    if nivel >= sub and sub > 1:
        caract.append(f"Subclasse (nível {sub}): escolha conforme o Livro do Jogador")
    if aumentos:
        caract.append(f"Aumentos de Atributo aplicados automaticamente: {len(aumentos)}x (+2)")
    if nivel >= 5 and d["classe"] in CLASSES_ATAQUE_EXTRA:
        caract.append("Ataque Extra (2 ataques por ação)")
    if nivel >= 5 and d["classe"] in ("Bardo", "Bruxo", "Clérigo", "Druida", "Feiticeiro", "Mago"):
        caract.append("Magias de 3º círculo ou superior disponíveis")
    if somar("talento"):
        caract.append("Talento inicial: escolha no Livro do Jogador (vantagem comprada)")
    if somar("resistencia"):
        caract.append("Resistência a um tipo de dano (definir com o mestre)")
    if nivel > 1:
        caract.append(f"Demais características até o nível {nivel}: consulte o Livro do Jogador")

    idiomas = list(raca["idiomas"]) + ["+1 idioma extra"] * somar("idioma")
    equipamento = list(classe["equip"])
    if somar("item"):
        equipamento.append("1 item mágico comum (definir com o mestre)")
    if somar("po"):
        equipamento.append(f"+{100 * somar('po')} po")
    if "Pobre" in desvs:
        equipamento.append("Sem moedas iniciais (desvantagem Pobre)")

    magia = info_magia(d["classe"], nivel, mods, prof)

    # 9) Resumo dos descontos
    lista_desv = [(n, DESVANTAGENS[n]["pts"], DESVANTAGENS[n]["desc"]) for n in desvs]
    lista_vant = [(n, VANTAGENS[n]["custo"], VANTAGENS[n]["desc"]) for n in vants]
    pontos = (sum(x[1] for x in lista_desv), sum(x[1] for x in lista_vant))

    return {
        **d,
        "base": base, "bonus_racial": bonus, "atrib": final, "mods": mods,
        "prof": prof, "pv": pv, "dado_vida": f"{nivel}d{dado}", "ca": ca_val, "ca_desc": ca_desc,
        "deslocamento": deslocamento, "tamanho": raca["tamanho"],
        "saves": saves, "pericias": pericias,
        "iniciativa": iniciativa, "percepcao_passiva": passiva,
        "ataque_corpo": mods["FOR"] + prof, "ataque_dist": mods["DES"] + prof,
        "tracos_raciais": raca["tracos"], "idiomas": idiomas,
        "caracteristicas": caract, "traco_antecedente": traco_ante,
        "equipamento": equipamento, "proficiencias": classe["profs"],
        "magia": magia, "log_rolagem": log,
        "desvantagens": lista_desv, "vantagens": lista_vant, "pontos": pontos,
        "notas_efeitos": notas, "inspiracao": somar("inspiracao") > 0,
    }


# ----------------------------------------------------------------------------
# FICHA EM TEXTO
# ----------------------------------------------------------------------------
def fmt_desl(v):
    return f"{v:g} m".replace(".", ",")


def ficha_texto(p):
    L = []
    linha = "=" * 64
    L += [linha, f" {p['nome'].upper()}".ljust(64), linha]
    L.append(f"Jogador: {p['jogador'] or '-'}")
    L.append(f"{p['raca']} {p['classe']} nível {p['nivel']}  |  Antecedente: {p['antecedente']}")
    L.append(f"Alinhamento: {p['alinhamento']}  |  Gênero: {p['genero']}")
    L.append(f"Idade: {p['idade']} anos  |  Altura: {p['altura']:.2f} m  |  Peso: {p['peso'] or '-'} kg")
    L.append(f"Tamanho: {p['tamanho']}")
    L += ["", "--- ATRIBUTOS " + "-" * 50]
    for a in ATRIBUTOS:
        L.append(f"{NOMES_ATRIBUTOS[a]:<14} ({a})  {p['atrib'][a]:>2}   mod {sg(p['mods'][a])}")
    L += ["", "--- COMBATE " + "-" * 52]
    L.append(f"Classe de Armadura: {p['ca']}  ({p['ca_desc']})")
    L.append(f"Pontos de Vida: {p['pv']}   Dados de Vida: {p['dado_vida']}")
    L.append(f"Iniciativa: {sg(p['iniciativa'])}   Deslocamento: {fmt_desl(p['deslocamento'])}")
    L.append(f"Bônus de Proficiência: {sg(p['prof'])}   Percepção Passiva: {p['percepcao_passiva']}")
    L.append(f"Ataque corpo a corpo (FOR): {sg(p['ataque_corpo'])}   À distância (DES): {sg(p['ataque_dist'])}")
    L.append("Salvaguardas de Morte:  Sucessos [ ][ ][ ]   Falhas [ ][ ][ ]")
    L.append("Inspiração: " + ("[X] (vantagem inicial)" if p["inspiracao"] else "[ ]"))
    L += ["", "--- SALVAGUARDAS " + "-" * 47]
    for a in ATRIBUTOS:
        s = p["saves"][a]
        L.append(f"[{'X' if s['prof'] else ' '}] {sg(s['mod']):>3}  {NOMES_ATRIBUTOS[a]}")
    L += ["", "--- PERÍCIAS " + "-" * 51]
    for nome, s in p["pericias"].items():
        marca = "E" if s["exp"] else "X" if s["prof"] else " "
        L.append(f"[{marca}] {sg(s['mod']):>3}  {nome} ({s['attr']})")
    L.append("(X = proficiente, E = especialista)")

    if p["magia"]:
        m = p["magia"]
        L += ["", "--- CONJURAÇÃO " + "-" * 49]
        L.append(f"Habilidade: {NOMES_ATRIBUTOS[m['habilidade']]}   CD: {m['cd']}   Ataque mágico: {sg(m['ataque'])}")
        if m["truques"]:
            L.append(f"Truques conhecidos: {m['truques']}")
        L.append(m["magias"])
        if m.get("pacto"):
            q, c = m["slots"][0]
            L.append(f"Espaços de Pacto: {q} de {c}º círculo (recuperam em descanso curto)")
        else:
            L.append("Espaços: " + "  ".join(f"{c}º x{q}" for c, q in m["slots"]))

    if p["desvantagens"] or p["vantagens"]:
        ganhos, gastos = p["pontos"]
        L += ["", f"--- DESCONTOS (ganhos: {ganhos} | gastos: {gastos}) ".ljust(64, "-")]
        if p["desvantagens"]:
            L.append("Desvantagens:")
            L += [f"  [+{pts}] {n}: {desc}" for n, pts, desc in p["desvantagens"]]
        if p["vantagens"]:
            L.append("Vantagens compradas:")
            L += [f"  [-{custo}] {n}: {desc}" for n, custo, desc in p["vantagens"]]
        if p["notas_efeitos"]:
            L.append("Efeitos aplicados:")
            L += [f"  * {n}" for n in p["notas_efeitos"]]
    L += ["", "--- CARACTERÍSTICAS DE CLASSE " + "-" * 34]
    L += [f"* {t}" for t in p["caracteristicas"]]
    L += ["", "--- TRAÇOS RACIAIS " + "-" * 45]
    L += [f"* {t}" for t in p["tracos_raciais"]]
    L += ["", f"Antecedente - {p['antecedente']}: {p['traco_antecedente']}"]
    L += ["", "--- PROFICIÊNCIAS E IDIOMAS " + "-" * 36]
    L.append(f"Armas/Armaduras: {p['proficiencias']}")
    L.append(f"Idiomas: {', '.join(p['idiomas'])}")
    L += ["", "--- EQUIPAMENTO INICIAL " + "-" * 40]
    L += [f"* {e}" for e in p["equipamento"]]
    L += ["", "--- ROLAGENS DOS ATRIBUTOS " + "-" * 37]
    L += p["log_rolagem"]
    L.append("Bônus raciais: " + (", ".join(f"{a} {sg(v)}" for a, v in p["bonus_racial"].items())))
    L.append(linha)
    return "\n".join(L)


# ----------------------------------------------------------------------------
# FICHA EM HTML (para impressão)
# ----------------------------------------------------------------------------
def ficha_html(p, auto_imprimir=False):
    e = html.escape

    def lista(itens):
        return "".join(f"<li>{e(i)}</li>" for i in itens)

    attrs = "".join(
        f"""<div class="attr"><div class="an">{e(NOMES_ATRIBUTOS[a])}</div>
        <div class="am">{sg(p['mods'][a])}</div><div class="av">{p['atrib'][a]}</div></div>"""
        for a in ATRIBUTOS)

    saves = "".join(
        f"<li><span class='dot {'on' if p['saves'][a]['prof'] else ''}'></span>"
        f"<b>{sg(p['saves'][a]['mod'])}</b> {e(NOMES_ATRIBUTOS[a])}</li>" for a in ATRIBUTOS)

    pericias = "".join(
        f"<li><span class='dot {'exp' if s['exp'] else 'on' if s['prof'] else ''}'></span>"
        f"<b>{sg(s['mod'])}</b> {e(n)} <small>({s['attr']})</small></li>"
        for n, s in p["pericias"].items())

    magia_html = ""
    if p["magia"]:
        m = p["magia"]
        if m.get("pacto"):
            q, c = m["slots"][0]
            slots = f"Espaços de Pacto: {q} de {c}º círculo"
        else:
            slots = "Espaços: " + " &nbsp; ".join(f"{c}º × {q}" for c, q in m["slots"])
        magia_html = f"""<div class="box"><h3>Conjuração</h3>
        <p>Habilidade: <b>{e(NOMES_ATRIBUTOS[m['habilidade']])}</b> &nbsp;|&nbsp; CD: <b>{m['cd']}</b>
        &nbsp;|&nbsp; Ataque mágico: <b>{sg(m['ataque'])}</b></p>
        <p>{('Truques: <b>%d</b> &nbsp;|&nbsp; ' % m['truques']) if m['truques'] else ''}{e(m['magias'])}</p>
        <p>{slots}</p></div>"""

    script = "<script>window.onload=function(){setTimeout(function(){window.print();},300);};</script>" \
        if auto_imprimir else ""

    insp = "background:#222" if p["inspiracao"] else ""
    extra_html = ""
    if p["desvantagens"] or p["vantagens"]:
        ganhos, gastos = p["pontos"]
        corpo = ""
        if p["desvantagens"]:
            corpo += "<p><b>Desvantagens</b></p><ul>" + "".join(
                f"<li>[+{pts}] <b>{e(n)}</b>: {e(desc)}</li>" for n, pts, desc in p["desvantagens"]) + "</ul>"
        if p["vantagens"]:
            corpo += "<p><b>Vantagens compradas</b></p><ul>" + "".join(
                f"<li>[-{custo}] <b>{e(n)}</b>: {e(desc)}</li>" for n, custo, desc in p["vantagens"]) + "</ul>"
        if p["notas_efeitos"]:
            corpo += "<p><b>Efeitos aplicados</b></p><ul>" + lista(p["notas_efeitos"]) + "</ul>"
        extra_html = f'<div class="box"><h3>Descontos (ganhos {ganhos} / gastos {gastos})</h3>{corpo}</div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Ficha - {e(p['nome'])}</title>
<style>
 @page {{ size: A4; margin: 10mm; }}
 * {{ box-sizing: border-box; }}
 body {{ font-family: Georgia, 'Times New Roman', serif; color:#222; margin:0; padding:12px; font-size:12px; }}
 h1 {{ margin:0; font-size:26px; border-bottom:3px double #7a1f1f; color:#7a1f1f; }}
 h3 {{ margin:0 0 6px; font-size:13px; text-transform:uppercase; letter-spacing:1px;
       color:#7a1f1f; border-bottom:1px solid #bbb; }}
 .head {{ display:grid; grid-template-columns:repeat(3,1fr); gap:4px 14px; margin:8px 0; }}
 .head div span {{ display:block; font-size:10px; color:#777; text-transform:uppercase; }}
 .grid {{ display:grid; grid-template-columns: 110px 1fr 1fr; gap:10px; align-items:start; }}
 .box {{ border:1.5px solid #7a1f1f; border-radius:6px; padding:8px; margin-bottom:10px; break-inside:avoid; }}
 .attr {{ text-align:center; border:1.5px solid #7a1f1f; border-radius:8px; margin-bottom:8px; padding:4px; }}
 .an {{ font-size:10px; text-transform:uppercase; }}
 .am {{ font-size:22px; font-weight:bold; }}
 .av {{ font-size:12px; border:1px solid #7a1f1f; border-radius:12px; display:inline-block;
        min-width:30px; background:#f6efe3; }}
 .stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; text-align:center; }}
 .stat {{ border:1px solid #999; border-radius:6px; padding:4px; }}
 .stat b {{ display:block; font-size:18px; }}
 .stat span {{ font-size:9px; text-transform:uppercase; color:#555; }}
 ul {{ margin:0; padding-left:16px; }}
 ul.sk {{ list-style:none; padding:0; }}
 ul.sk li {{ line-height:1.55; }}
 .dot {{ display:inline-block; width:9px; height:9px; border:1px solid #333; border-radius:50%;
         margin-right:4px; }}
 .dot.on {{ background:#222; }}
 .dot.exp {{ background:#7a1f1f; border-color:#7a1f1f; }}
 .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
 small {{ color:#777; }}
 p {{ margin:3px 0; }}
 .morte {{ margin-top:6px; }}
 .cx {{ display:inline-block; width:11px; height:11px; border:1px solid #333; border-radius:50%; margin:0 2px; }}
 @media print {{ body {{ padding:0; }} }}
</style></head><body>
<h1>{e(p['nome'])}</h1>
<div class="head">
 <div><span>Classe e nível</span>{e(p['classe'])} {p['nivel']}</div>
 <div><span>Raça</span>{e(p['raca'])} ({e(p['tamanho'])})</div>
 <div><span>Antecedente</span>{e(p['antecedente'])}</div>
 <div><span>Jogador</span>{e(p['jogador'] or '-')}</div>
 <div><span>Alinhamento</span>{e(p['alinhamento'])}</div>
 <div><span>Gênero</span>{e(p['genero'])}</div>
 <div><span>Idade</span>{p['idade']} anos</div>
 <div><span>Altura</span>{p['altura']:.2f} m</div>
 <div><span>Peso</span>{e(str(p['peso'] or '-'))} kg</div>
</div>

<div class="grid">
 <div>{attrs}</div>
 <div>
  <div class="box"><div class="stats">
    <div class="stat"><b>{p['ca']}</b><span>Classe de Armadura</span></div>
    <div class="stat"><b>{sg(p['iniciativa'])}</b><span>Iniciativa</span></div>
    <div class="stat"><b>{e(fmt_desl(p['deslocamento']))}</b><span>Deslocamento</span></div>
    <div class="stat"><b>{p['pv']}</b><span>PV máximos</span></div>
    <div class="stat"><b>{e(p['dado_vida'])}</b><span>Dados de Vida</span></div>
    <div class="stat"><b>{sg(p['prof'])}</b><span>Proficiência</span></div>
    <div class="stat"><b>{sg(p['ataque_corpo'])}</b><span>Ataque C.a.C.</span></div>
    <div class="stat"><b>{sg(p['ataque_dist'])}</b><span>Ataque Distância</span></div>
    <div class="stat"><b>{p['percepcao_passiva']}</b><span>Percepção Passiva</span></div>
   </div>
   <p><small>{e(p['ca_desc'])}</small></p>
   <p class="morte">PV atuais: ________ &nbsp; PV temp.: ________ &nbsp; Inspiração: <span class="cx" style="{insp}"></span></p>
   <p class="morte">Salv. de Morte — Sucessos: <span class="cx"></span><span class="cx"></span><span class="cx"></span>
   &nbsp; Falhas: <span class="cx"></span><span class="cx"></span><span class="cx"></span></p>
  </div>
  <div class="box"><h3>Salvaguardas</h3><ul class="sk">{saves}</ul></div>
  <div class="box"><h3>Características de Classe</h3><ul>{lista(p['caracteristicas'])}</ul></div>
  {magia_html}
 </div>
 <div>
  <div class="box"><h3>Perícias</h3><ul class="sk">{pericias}</ul>
   <p><small>● proficiente &nbsp; <span style="color:#7a1f1f">●</span> especialista</small></p></div>
 </div>
</div>

{extra_html}
<div class="cols">
 <div class="box"><h3>Traços Raciais</h3><ul>{lista(p['tracos_raciais'])}</ul>
  <p><b>{e(p['antecedente'])}:</b> {e(p['traco_antecedente'])}</p></div>
 <div class="box"><h3>Equipamento</h3><ul>{lista(p['equipamento'])}</ul></div>
</div>
<div class="box"><h3>Proficiências e Idiomas</h3>
 <p><b>Armas e armaduras:</b> {e(p['proficiencias'])}</p>
 <p><b>Idiomas:</b> {e(', '.join(p['idiomas']))}</p></div>
<div class="box"><h3>Anotações</h3><div style="height:70px"></div></div>
{script}
</body></html>"""


# ----------------------------------------------------------------------------
# ROLADOR DE DADOS
# ----------------------------------------------------------------------------
def rolar_expressao(expr):
    """Interpreta '2d6+1d4+3' e devolve (total, descrição). Levanta ValueError se inválida."""
    limpa = expr.replace(" ", "").lower()
    if not limpa:
        raise ValueError("Expressão vazia.")
    tokens = re.findall(r"[+-]?\d*d\d+|[+-]?\d+", limpa)
    if "".join(tokens) != limpa:
        raise ValueError("Use o formato 2d6+3 (ex.: d20, 4d6, 1d8+2).")
    total, partes = 0, []
    for t in tokens:
        sinal = -1 if t.startswith("-") else 1
        t = t.lstrip("+-")
        if "d" in t:
            q, lados = t.split("d")
            q = int(q) if q else 1
            lados = int(lados)
            if not (1 <= q <= 100 and 2 <= lados <= 1000):
                raise ValueError("Máximo de 100 dados e 1000 lados.")
            res = [random.randint(1, lados) for _ in range(q)]
            total += sinal * sum(res)
            partes.append(f"{'-' if sinal < 0 else ''}{q}d{lados}{res}")
        else:
            total += sinal * int(t)
            partes.append(f"{'-' if sinal < 0 else '+'}{t}")
    return total, " ".join(partes)


# ----------------------------------------------------------------------------
# INTERFACE
# ----------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.personagem = None
        self.testes = {}
        root.title("Gerador de Ficha - D&D 5e")
        root.config(bg=MARROM)

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=6, pady=6)
        self.aba_criar = tk.Frame(self.nb, bg=MARROM)
        self.aba_desc = tk.Frame(self.nb, bg=MARROM)
        self.aba_ficha = tk.Frame(self.nb, bg=MARROM)
        self.aba_dados = tk.Frame(self.nb, bg=MARROM)
        self.nb.add(self.aba_criar, text="Criação")
        self.nb.add(self.aba_desc, text="Descontos")
        self.nb.add(self.aba_ficha, text="Ficha")
        self.nb.add(self.aba_dados, text="Dados")

        self._montar_criacao()
        self._montar_descontos()
        self._montar_ficha()
        self._montar_dados()
        self.atualizar_resumo_classe()

    # ---------- Aba criação ----------
    def _label(self, parent, texto, linha):
        tk.Label(parent, text=texto, bg=MARROM, fg="white").grid(row=linha, column=0, sticky="w", pady=4, padx=8)

    def _combo(self, parent, var, valores, linha, largura=32):
        cb = ttk.Combobox(parent, textvariable=var, values=valores, state="readonly", width=largura)
        cb.grid(row=linha, column=1, pady=4, padx=8, sticky="w")
        return cb

    def _montar_criacao(self):
        f = self.aba_criar
        self.v = {
            "nome": tk.StringVar(), "jogador": tk.StringVar(), "idade": tk.StringVar(value="25"),
            "altura": tk.StringVar(value="1.75"), "peso": tk.StringVar(),
            "genero": tk.StringVar(value="Masculino"),
            "raca": tk.StringVar(value="Humano"), "classe": tk.StringVar(value="Guerreiro"),
            "antecedente": tk.StringVar(value="Soldado"),
            "alinhamento": tk.StringVar(value="Aleatório"),
            "nivel": tk.IntVar(value=1),
            "metodo": tk.StringVar(value="4d6 (descarta o menor)"),
            "distribuicao": tk.StringVar(value="Otimizada para a classe"),
            "pv_metodo": tk.StringVar(value="Valor médio"),
        }
        v = self.v
        linhas = [
            ("Nome do personagem:", "entry", "nome"),
            ("Nome do jogador:", "entry", "jogador"),
            ("Idade:", "entry", "idade"),
            ("Altura (em metros):", "entry", "altura"),
            ("Peso (kg, opcional):", "entry", "peso"),
        ]
        r = 0
        for texto, _, chave in linhas:
            self._label(f, texto, r)
            ttk.Entry(f, textvariable=v[chave], width=35).grid(row=r, column=1, pady=4, padx=8, sticky="w")
            r += 1

        self._label(f, "Gênero:", r)
        self._combo(f, v["genero"], ["Masculino", "Feminino", "Outro"], r); r += 1
        self._label(f, "Raça:", r)
        self._combo(f, v["raca"], list(RACAS.keys()), r); r += 1
        self._label(f, "Classe:", r)
        cb = self._combo(f, v["classe"], list(CLASSES.keys()), r)
        cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar_resumo_classe()); r += 1
        self.resumo_classe = tk.Label(f, text="", bg=MARROM, fg="#ffe9b0", justify="left", wraplength=360)
        self.resumo_classe.grid(row=r, column=0, columnspan=2, sticky="w", padx=8); r += 1
        self._label(f, "Antecedente:", r)
        self._combo(f, v["antecedente"], list(ANTECEDENTES.keys()), r); r += 1
        self._label(f, "Alinhamento:", r)
        self._combo(f, v["alinhamento"], ["Aleatório"] + ALINHAMENTOS, r); r += 1
        self._label(f, "Nível (1-20):", r)
        ttk.Spinbox(f, from_=1, to=20, textvariable=v["nivel"], width=8).grid(row=r, column=1, pady=4, padx=8, sticky="w"); r += 1
        self._label(f, "Geração de atributos:", r)
        self._combo(f, v["metodo"], ["4d6 (descarta o menor)", "3d6 clássico",
                                     "Array padrão (15,14,13,12,10,8)"], r); r += 1
        self._label(f, "Distribuição:", r)
        self._combo(f, v["distribuicao"], ["Otimizada para a classe", "Ordem aleatória"], r); r += 1
        self._label(f, "Pontos de vida (nív. 2+):", r)
        self._combo(f, v["pv_metodo"], ["Valor médio", "Rolar dado"], r); r += 1

        tk.Button(f, text="🎲 Gerar Personagem", command=self.gerar, font=("Arial", 11, "bold"),
                  padx=10, pady=4).grid(row=r, column=0, columnspan=2, pady=16)

    def atualizar_resumo_classe(self):
        c = CLASSES[self.v["classe"].get()]
        conj = {"cheio": "Conjurador", "meio": "Meio-conjurador", "pacto": "Magia de Pacto", None: "Não conjurador"}[c["conj"]]
        self.resumo_classe.config(
            text=f"d{c['dado']} de vida • Salvaguardas: {', '.join(c['salvaguardas'])} • "
                 f"{conj} • {c['n_pericias']} perícias")

    def gerar(self):
        v = self.v
        try:
            idade = int(v["idade"].get())
            if idade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira uma idade válida (número inteiro).")
            return
        try:
            altura = float(v["altura"].get().replace(",", "."))
            if altura <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira uma altura válida (ex.: 1.75).")
            return
        try:
            nivel = int(v["nivel"].get())
            if not 1 <= nivel <= 20:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Erro", "O nível deve ser um número entre 1 e 20.")
            return

        ganhos, gastos, desv_sel, vant_sel = self.calcular_pontos()
        if len(vant_sel) > MAX_VANTAGENS:
            messagebox.showerror("Descontos", f"Você pode escolher no máximo {MAX_VANTAGENS} vantagens.")
            self.nb.select(self.aba_desc)
            return
        if gastos > ganhos:
            messagebox.showerror("Descontos", f"Você gastou {gastos} pontos em vantagens, "
                                              f"mas só ganhou {ganhos} com desvantagens.")
            self.nb.select(self.aba_desc)
            return

        alinh = v["alinhamento"].get()
        if alinh == "Aleatório":
            alinh = random.choice(ALINHAMENTOS)

        dados = {
            "nome": v["nome"].get().strip() or "Aventureiro sem nome",
            "jogador": v["jogador"].get().strip(), "idade": idade, "altura": altura,
            "peso": v["peso"].get().strip(), "genero": v["genero"].get(),
            "raca": v["raca"].get(), "classe": v["classe"].get(),
            "antecedente": v["antecedente"].get(), "alinhamento": alinh, "nivel": nivel,
            "metodo": v["metodo"].get(), "distribuicao": v["distribuicao"].get(),
            "pv_metodo": v["pv_metodo"].get(),
            "desv_sel": desv_sel, "vant_sel": vant_sel,
        }
        self.personagem = criar_personagem(dados)
        self.mostrar_ficha()
        self.atualizar_testes()
        self.nb.select(self.aba_ficha)

    # ---------- Aba descontos ----------
    def _montar_descontos(self):
        f = self.aba_desc
        self.desv_nomes = list(DESVANTAGENS.keys())
        self.vant_nomes = list(VANTAGENS.keys())
        self.desv_sorteadas = []
        self._vant_prev = set()

        tk.Label(f, justify="left", wraplength=680, bg=MARROM, fg="#ffe9b0",
                 text=(f"1) Clique em \"Sortear desvantagens\": o jogo sorteia {DESV_MIN} ou {DESV_MAX} "
                       f"desvantagens, que dão pontos.\n2) Com esses pontos, escolha você mesmo até "
                       f"{MAX_VANTAGENS} vantagens. Clique num item para ver a descrição.")
                 ).pack(padx=10, pady=8, anchor="w")

        corpo = tk.Frame(f, bg=MARROM)
        corpo.pack(fill="both", expand=True, padx=8)
        esq = tk.Frame(corpo, bg=MARROM)
        esq.pack(side="left", fill="both", expand=True, padx=4)
        dire = tk.Frame(corpo, bg=MARROM)
        dire.pack(side="left", fill="both", expand=True, padx=4)

        tk.Label(esq, text="Desvantagens sorteadas (dão pontos)", bg=MARROM, fg="white",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.lb_desv = tk.Listbox(esq, selectmode="browse", exportselection=False, width=34, height=17)
        self.lb_desv.pack(fill="both", expand=True)

        tk.Label(dire, text=f"Vantagens (escolha até {MAX_VANTAGENS})", bg=MARROM, fg="white",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.lb_vant = tk.Listbox(dire, selectmode="multiple", exportselection=False, width=34, height=17)
        for n in self.vant_nomes:
            self.lb_vant.insert("end", f"[-{VANTAGENS[n]['custo']}] {n}")
        self.lb_vant.pack(fill="both", expand=True)

        self.lb_vant.bind("<<ListboxSelect>>", lambda e: self.ao_selecionar_vantagem())
        self.lb_desv.bind("<ButtonRelease-1>",
                          lambda e: self.mostrar_desc(self.lb_desv, DESVANTAGENS, self.desv_sorteadas, e))
        self.lb_vant.bind("<ButtonRelease-1>",
                          lambda e: self.mostrar_desc(self.lb_vant, VANTAGENS, self.vant_nomes, e))

        self.lbl_desc = tk.Label(f, text="", justify="left", wraplength=680, bg=MARROM, fg="white", height=3)
        self.lbl_desc.pack(padx=10, pady=4, anchor="w")
        self.lbl_pontos = tk.Label(f, text="", bg=MARROM, fg="white", font=("Arial", 11, "bold"))
        self.lbl_pontos.pack(pady=4)

        bar = tk.Frame(f, bg=MARROM)
        bar.pack(pady=(0, 10))
        tk.Button(bar, text=f"🎲 Sortear desvantagens ({DESV_MIN} ou {DESV_MAX})",
                  command=self.sortear_desvantagens, padx=6).pack(side="left", padx=4)
        tk.Button(bar, text="Limpar vantagens", command=self.limpar_vantagens, padx=6).pack(side="left", padx=4)
        tk.Button(bar, text="Limpar tudo", command=self.limpar_descontos, padx=6).pack(side="left", padx=4)
        self.atualizar_pontos()

    def mostrar_desc(self, lb, tabela, nomes, evento):
        i = lb.nearest(evento.y)
        if 0 <= i < len(nomes):
            self.lbl_desc.config(text=f"{nomes[i]}: {tabela[nomes[i]]['desc']}")

    def calcular_pontos(self):
        desv = list(self.desv_sorteadas)
        vant = [self.vant_nomes[i] for i in self.lb_vant.curselection()]
        ganhos = sum(DESVANTAGENS[n]["pts"] for n in desv)
        gastos = sum(VANTAGENS[n]["custo"] for n in vant)
        return ganhos, gastos, desv, vant

    def atualizar_pontos(self):
        ganhos, gastos, _, vant = self.calcular_pontos()
        invalido = gastos > ganhos or len(vant) > MAX_VANTAGENS
        self.lbl_pontos.config(
            text=(f"Pontos ganhos: {ganhos}   |   Gastos: {gastos}   |   Saldo: {ganhos - gastos}"
                  f"   |   Vantagens: {len(vant)}/{MAX_VANTAGENS}"),
            fg="#ff9a9a" if invalido else "white")

    def ao_selecionar_vantagem(self):
        """Impede passar do máximo de vantagens ou do saldo de pontos."""
        ganhos = sum(DESVANTAGENS[n]["pts"] for n in self.desv_sorteadas)
        atual = set(self.lb_vant.curselection())
        aviso = ""
        for i in sorted(atual - self._vant_prev):
            custo_total = sum(VANTAGENS[self.vant_nomes[j]]["custo"] for j in atual)
            if not self.desv_sorteadas:
                aviso = "Sorteie as desvantagens primeiro: elas dão os pontos para comprar vantagens."
            elif len(atual) > MAX_VANTAGENS:
                aviso = f"Máximo de {MAX_VANTAGENS} vantagens."
            elif custo_total > ganhos:
                aviso = "Pontos insuficientes para essa vantagem."
            else:
                continue
            self.lb_vant.selection_clear(i)
            atual.discard(i)
        self._vant_prev = atual
        if aviso:
            self.lbl_desc.config(text=aviso)
        self.atualizar_pontos()

    def sortear_desvantagens(self):
        self.desv_sorteadas = random.sample(self.desv_nomes, random.randint(DESV_MIN, DESV_MAX))
        self.lb_desv.delete(0, "end")
        for n in self.desv_sorteadas:
            self.lb_desv.insert("end", f"[+{DESVANTAGENS[n]['pts']}] {n}")
        ganhos, gastos, _, _ = self.calcular_pontos()
        texto = "Desvantagens sorteadas! Clique em uma para ver a descrição."
        if gastos > ganhos:
            self.lb_vant.selection_clear(0, "end")
            self._vant_prev = set()
            texto = "Desvantagens sorteadas. As vantagens foram desmarcadas porque os pontos mudaram."
        self.lbl_desc.config(text=texto)
        self.atualizar_pontos()

    def limpar_vantagens(self):
        self.lb_vant.selection_clear(0, "end")
        self._vant_prev = set()
        self.atualizar_pontos()

    def limpar_descontos(self):
        self.desv_sorteadas = []
        self.lb_desv.delete(0, "end")
        self.lb_vant.selection_clear(0, "end")
        self._vant_prev = set()
        self.lbl_desc.config(text="")
        self.atualizar_pontos()

    # ---------- Aba ficha ----------
    def _montar_ficha(self):
        f = self.aba_ficha
        self.texto = scrolledtext.ScrolledText(f, width=76, height=34, font=("Courier New", 10), wrap="none")
        self.texto.pack(fill="both", expand=True, padx=8, pady=8)
        self.texto.insert("1.0", "Gere um personagem na aba Criação para ver a ficha aqui.")
        self.texto.config(state="disabled")

        bar = tk.Frame(f, bg=MARROM)
        bar.pack(pady=(0, 8))
        for txt, cmd in [("🖨 Imprimir ficha", self.imprimir), ("Salvar HTML", self.salvar_html),
                         ("Salvar TXT", self.salvar_txt), ("Copiar texto", self.copiar),
                         ("Rolar atributos de novo", self.gerar)]:
            tk.Button(bar, text=txt, command=cmd, padx=6).pack(side="left", padx=4)

    def mostrar_ficha(self):
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", ficha_texto(self.personagem))
        self.texto.config(state="disabled")

    def _precisa_personagem(self):
        if not self.personagem:
            messagebox.showinfo("Ficha", "Gere um personagem primeiro.")
            return False
        return True

    def imprimir(self):
        """Abre a ficha no navegador e dispara a janela de impressão."""
        if not self._precisa_personagem():
            return
        try:
            fd, caminho = tempfile.mkstemp(suffix=".html", prefix="ficha_dnd_")
            with os.fdopen(fd, "w", encoding="utf-8") as arq:
                arq.write(ficha_html(self.personagem, auto_imprimir=True))
            webbrowser.open("file://" + os.path.abspath(caminho))
        except Exception as err:
            messagebox.showerror("Erro", f"Não foi possível abrir a impressão:\n{err}")

    def salvar_html(self):
        if not self._precisa_personagem():
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("HTML", "*.html")],
            initialfile=f"ficha_{self.personagem['nome']}.html")
        if caminho:
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write(ficha_html(self.personagem))
            messagebox.showinfo("Salvo", "Ficha salva. Abra no navegador e use Ctrl+P para imprimir ou gerar PDF.")

    def salvar_txt(self):
        if not self._precisa_personagem():
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Texto", "*.txt")],
            initialfile=f"ficha_{self.personagem['nome']}.txt")
        if caminho:
            with open(caminho, "w", encoding="utf-8") as arq:
                arq.write(ficha_texto(self.personagem))
            messagebox.showinfo("Salvo", "Ficha salva em texto.")

    def copiar(self):
        if not self._precisa_personagem():
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(ficha_texto(self.personagem))
        messagebox.showinfo("Copiado", "Ficha copiada para a área de transferência.")

    # ---------- Aba dados ----------
    def _montar_dados(self):
        f = self.aba_dados
        self.modo = tk.StringVar(value="normal")

        topo = tk.Frame(f, bg=MARROM)
        topo.pack(pady=8)
        tk.Label(topo, text="Dados rápidos:", bg=MARROM, fg="white").grid(row=0, column=0, padx=4)
        for i, lados in enumerate([4, 6, 8, 10, 12, 20, 100]):
            tk.Button(topo, text=f"d{lados}", width=5,
                      command=lambda l=lados: self.rolar(f"1d{l}")).grid(row=0, column=i + 1, padx=2)

        mid = tk.Frame(f, bg=MARROM)
        mid.pack(pady=4)
        tk.Label(mid, text="Expressão:", bg=MARROM, fg="white").grid(row=0, column=0, padx=4)
        self.expr = tk.StringVar(value="1d20")
        e = ttk.Entry(mid, textvariable=self.expr, width=22)
        e.grid(row=0, column=1, padx=4)
        e.bind("<Return>", lambda ev: self.rolar(self.expr.get()))
        tk.Button(mid, text="Rolar", command=lambda: self.rolar(self.expr.get())).grid(row=0, column=2, padx=4)

        modos = tk.Frame(f, bg=MARROM)
        modos.pack()
        for texto, val in [("Normal", "normal"), ("Vantagem", "vantagem"), ("Desvantagem", "desvantagem")]:
            tk.Radiobutton(modos, text=texto, value=val, variable=self.modo, bg=MARROM, fg="white",
                           selectcolor="#5a2d0c", activebackground=MARROM,
                           activeforeground="white").pack(side="left", padx=6)

        teste = tk.Frame(f, bg=MARROM)
        teste.pack(pady=8)
        tk.Label(teste, text="Teste da ficha:", bg=MARROM, fg="white").grid(row=0, column=0, padx=4)
        self.teste_var = tk.StringVar()
        self.teste_cb = ttk.Combobox(teste, textvariable=self.teste_var, state="readonly", width=30)
        self.teste_cb.grid(row=0, column=1, padx=4)
        tk.Button(teste, text="Rolar d20 + mod.", command=self.rolar_teste).grid(row=0, column=2, padx=4)

        self.log = scrolledtext.ScrolledText(f, width=70, height=20, font=("Courier New", 10), state="disabled")
        self.log.pack(padx=8, pady=8, fill="both", expand=True)
        tk.Button(f, text="Limpar histórico", command=self.limpar_log).pack(pady=(0, 8))

    def atualizar_testes(self):
        p = self.personagem
        self.testes = {"Iniciativa": p["iniciativa"]}
        for a in ATRIBUTOS:
            self.testes[f"Teste de {NOMES_ATRIBUTOS[a]}"] = p["mods"][a]
        for a in ATRIBUTOS:
            self.testes[f"Salvaguarda de {NOMES_ATRIBUTOS[a]}"] = p["saves"][a]["mod"]
        for nome, s in p["pericias"].items():
            self.testes[nome] = s["mod"]
        self.testes["Ataque corpo a corpo"] = p["ataque_corpo"]
        self.testes["Ataque à distância"] = p["ataque_dist"]
        if p["magia"]:
            self.testes["Ataque mágico"] = p["magia"]["ataque"]
        self.teste_cb["values"] = list(self.testes.keys())
        self.teste_var.set("Iniciativa")

    def escrever_log(self, texto):
        self.log.config(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def limpar_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def rolar(self, expr, rotulo=None):
        try:
            modo = self.modo.get()
            t1, d1 = rolar_expressao(expr)
            prefixo = f"{rotulo}: " if rotulo else ""
            if modo == "normal":
                self.escrever_log(f"{prefixo}{expr} -> {d1} = {t1}")
            else:
                t2, d2 = rolar_expressao(expr)
                escolhido = max(t1, t2) if modo == "vantagem" else min(t1, t2)
                self.escrever_log(f"{prefixo}{expr} com {modo}: [{d1} = {t1}] [{d2} = {t2}] -> {escolhido}")
        except ValueError as err:
            messagebox.showerror("Expressão inválida", str(err))

    def rolar_teste(self):
        nome = self.teste_var.get()
        if not nome:
            messagebox.showinfo("Teste", "Gere um personagem e escolha um teste.")
            return
        mod = self.testes[nome]
        self.rolar(f"1d20{mod:+d}" if mod else "1d20", rotulo=nome)


if __name__ == "__main__":
    janela = tk.Tk()
    App(janela)
    janela.mainloop()
