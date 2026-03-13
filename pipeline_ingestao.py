import re
import json
from sqlalchemy.orm import sessionmaker

# Importamos as configurações e tabelas do seu outro arquivo!
# Isso é a verdadeira interoperabilidade em ação.
from database_schema import engine, Questao, Assunto

def extrair_questao_multipla_escolha(texto):
    """Extrai enunciado e alternativas usando RegEx."""
    padrao_enunciado = r'\d+\.\s*(.*?)(?=\nA\))'
    match_enunciado = re.search(padrao_enunciado, texto, re.DOTALL)
    enunciado_limpo = match_enunciado.group(1).strip() if match_enunciado else "Enunciado não encontrado."

    padrao_alternativas = r'([A-E])\)\s*(.*?)(?=\n[A-E]\)|\Z)'
    matches_alternativas = re.findall(padrao_alternativas, texto, re.DOTALL)

    dicionario_alternativas = {}
    for letra, texto_alt in matches_alternativas:
        dicionario_alternativas[letra] = texto_alt.strip()

    return enunciado_limpo, dicionario_alternativas

def processar_e_salvar_questao(texto_bruto, banca, ano, gabarito, comentario, id_assunto):
    """Junta o extrator com o banco de dados e salva a questão."""
    print("Processando o texto bruto...")
    enunciado, alternativas = extrair_questao_multipla_escolha(texto_bruto)
    
    # Abre a conexão com o banco
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Cria o objeto da questão pronto para o banco
        nova_questao = Questao(
            banca=banca,
            ano=ano,
            id_assunto=id_assunto,
            modalidade="ME",
            enunciado=enunciado,
            alternativas=alternativas, # O SQLAlchemy converte esse dicionário em JSON automaticamente!
            gabarito=gabarito,
            comentario_teorico=comentario
        )
        
        # Adiciona e confirma a transação
        session.add(nova_questao)
        session.commit()
        print(f"✅ Sucesso! Questão da banca {banca} inserida no banco de dados.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao salvar no banco: {e}")
        
    finally:
        session.close()

# ==========================================
# TESTANDO O PIPELINE NA PRÁTICA
# ==========================================
if __name__ == "__main__":
    # Um texto copiado de uma prova de Controle Interno/AFO
    texto_prova_copiado = """
1. Segundo a Lei de Responsabilidade Fiscal (LRF), a despesa total com pessoal, em cada período de apuração, não poderá exceder os percentuais da receita corrente líquida. No caso dos Municípios, esse limite máximo é de:
A) 50%.
B) 54%.
C) 60%.
D) 65%.
E) 70%.
    """
    
    # Parâmetros que você preencheria rapidamente (ou puxaria de uma planilha de controle)
    processar_e_salvar_questao(
        texto_bruto=texto_prova_copiado,
        banca="FGV",
        ano=2024,
        gabarito="C",
        comentario="Correto. Conforme o Art. 19, inciso III da LRF, o limite para Municípios é de 60%.",
        id_assunto=1 # Supondo que o ID 1 seja AFO/LRF no seu banco
    )

import re

def extrair_questao_certo_errado(texto):
    """
    Extrai apenas o enunciado de uma questão estilo Certo/Errado.
    Lógica RegEx: Procura por dígitos, um ponto, e captura todo o resto do texto.
    """
    padrao_enunciado = r'\d+\.\s*(.*)'
    match = re.search(padrao_enunciado, texto, re.DOTALL)
    
    # Se encontrar o padrão, limpa os espaços. Se não, retorna o texto original limpo.
    enunciado_limpo = match.group(1).strip() if match else texto.strip()
    
    return enunciado_limpo

# --- TESTANDO O EXTRATOR C/E ---
if __name__ == "__main__":
    texto_ce_copiado = """
    1. O controle interno, no âmbito da administração pública, deve ser exercido de forma prévia, concomitante e a posteriori, visando garantir a legalidade e a eficiência da gestão dos recursos.
    """
    
    enunciado = extrair_questao_certo_errado(texto_ce_copiado)
    
    print("🎯 ENUNCIADO C/E EXTRAÍDO:")
    print(enunciado)