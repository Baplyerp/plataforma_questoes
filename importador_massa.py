import re
import json
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao

def processar_arquivo_txt(caminho_arquivo, banca, ano, id_assunto):
    """Lê o TXT, separa as questões e salva no banco de dados."""
    
    # Lê o conteúdo do arquivo txt
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            texto_completo = file.read()
    except FileNotFoundError:
        print(f"❌ Arquivo '{caminho_arquivo}' não encontrado. Crie o arquivo e cole as questões lá!")
        return

    # O RegEx mágico que separa cada bloco de questão (começa com número e ponto, vai até a palavra 'Comentário: ...')
    padrao_blocos = r'(\d+\.\s+.*?Comentário:\s*.*?)(?=\n\n\d+\.|\Z)'
    blocos = re.findall(padrao_blocos, texto_completo, re.DOTALL)
    
    print(f"🔍 Encontradas {len(blocos)} questões no arquivo. Iniciando importação...")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    questoes_inseridas = 0

    for bloco in blocos:
        try:
            # 1. Extrai Gabarito e Comentário (que ficam no final do bloco)
            gabarito = re.search(r'Gabarito:\s*([A-Ea-eCcEe])', bloco).group(1).upper()
            comentario = re.search(r'Comentário:\s*(.*)', bloco, re.DOTALL).group(1).strip()
            
            # Remove a parte do gabarito e comentário para analisar só a pergunta
            texto_pergunta = re.sub(r'\nGabarito:.*', '', bloco, flags=re.DOTALL).strip()
            
            # 2. Descobre se é Múltipla Escolha ou C/E
            # Se encontrar o padrão "A) texto", é múltipla escolha
            padrao_alternativas = r'([A-E])\)\s*(.*?)(?=\n[A-E]\)|\Z)'
            matches_alternativas = re.findall(padrao_alternativas, texto_pergunta, re.DOTALL)
            
            if matches_alternativas:
                modalidade = "ME"
                # O enunciado é tudo antes da letra A)
                enunciado = re.search(r'\d+\.\s*(.*?)(?=\nA\))', texto_pergunta, re.DOTALL).group(1).strip()
                alternativas = {letra: texto.strip() for letra, texto in matches_alternativas}
            else:
                modalidade = "CE"
                # O enunciado é o texto inteiro (tirando o número da frente)
                enunciado = re.search(r'\d+\.\s*(.*)', texto_pergunta, re.DOTALL).group(1).strip()
                alternativas = None # C/E não tem alternativas

            # 3. Cria o objeto e salva no banco
            nova_questao = Questao(
                banca=banca, ano=ano, id_assunto=id_assunto,
                modalidade=modalidade, enunciado=enunciado,
                alternativas=alternativas, gabarito=gabarito,
                comentario_teorico=comentario
            )
            session.add(nova_questao)
            questoes_inseridas += 1
            
        except Exception as e:
            print(f"⚠️ Erro ao processar uma das questões. Verifique a formatação. Erro técnico: {e}")

    # Confirma todas as inserções no banco
    session.commit()
    session.close()
    print(f"✅ Sucesso! {questoes_inseridas} questões foram salvas no banco de dados.")

# ==========================================
# EXECUTANDO O IMPORTADOR
# ==========================================
if __name__ == "__main__":
    # Ajuste os dados da bateria de questões aqui antes de rodar!
    processar_arquivo_txt(
        caminho_arquivo='questoes_brutas.txt',
        banca='Minha Revisão',
        ano=2026,
        id_assunto=1 # Lembre-se que o ID 1 foi o que criamos para AFO/Controle
    )