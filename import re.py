import re
import json

# 1. O Texto Bruto (Simulando o "Copiar e Colar" de um PDF de prova)
texto_bruto_copiado = """
1. Sobre a formação histórica do município, assinale a alternativa que indica corretamente o local em torno do qual a cidade se desenvolveu:
A) Engenho Catende, que serviu como marco zero da região.
B) Engenho Milagre da Conceição, onde os primeiros povoados se estabeleceram.
C) Fazenda Água Branca, devido à proximidade com o rio.
D) Ao redor da antiga estação ferroviária central.
E) Nenhuma das alternativas anteriores.
"""

def extrair_questao_multipla_escolha(texto):
    """
    Função que recebe um texto bruto e retorna o enunciado e um 
    dicionário com as alternativas.
    """
    
    # Passo A: Extrair o Enunciado
    # Lógica RegEx: Procure um número (\d+), um ponto (\.), e capture tudo (.*?) 
    # até encontrar uma quebra de linha seguida de "A)" (?=\nA\)).
    padrao_enunciado = r'\d+\.\s*(.*?)(?=\nA\))'
    match_enunciado = re.search(padrao_enunciado, texto, re.DOTALL)
    
    # Limpa os espaços em branco nas pontas
    enunciado_limpo = match_enunciado.group(1).strip() if match_enunciado else "Enunciado não encontrado."

    # Passo B: Extrair as Alternativas
    # Lógica RegEx: Capture a letra ([A-E]), o parêntese (\)), e capture o texto (.*?) 
    # até encontrar a próxima quebra de linha com outra letra ou o fim do texto (\Z).
    padrao_alternativas = r'([A-E])\)\s*(.*?)(?=\n[A-E]\)|\Z)'
    matches_alternativas = re.findall(padrao_alternativas, texto, re.DOTALL)

    # Passo C: Montar o formato JSON (Dicionário Python)
    dicionario_alternativas = {}
    for letra, texto_alt in matches_alternativas:
        dicionario_alternativas[letra] = texto_alt.strip()

    return enunciado_limpo, dicionario_alternativas

# --- EXECUTANDO O TESTE ---
enunciado, alternativas = extrair_questao_multipla_escolha(texto_bruto_copiado)

print("🎯 ENUNCIADO EXTRAÍDO:")
print(enunciado)
print("\n🧩 ALTERNATIVAS ESTRUTURADAS (Prontas para o Banco de Dados):")
# O json.dumps aqui é só para imprimir bonito na tela para você ver
print(json.dumps(alternativas, indent=4, ensure_ascii=False))