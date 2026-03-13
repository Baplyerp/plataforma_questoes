import re
import json
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao

def processar_arquivo_txt(caminho_arquivo, banca, ano, id_assunto):
    """Lê o TXT, separa as questões e salva no banco de dados."""
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            texto_completo = file.read()
    except FileNotFoundError:
        print(f"❌ Arquivo '{caminho_arquivo}' não encontrado. Crie o arquivo e cole as questões lá!")
        return

    padrao_blocos = r'(\d+\.\s+.*?Comentário:\s*.*?)(?=\n\n\d+\.|\Z)'
    blocos = re.findall(padrao_blocos, texto_completo, re.DOTALL)
    
    print(f"🔍 Encontradas {len(blocos)} questões no arquivo. Iniciando importação...")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    questoes_inseridas = 0

    for bloco in blocos:
        try:
            gabarito = re.search(r'Gabarito:\s*([A-Ea-eCcEe])', bloco).group(1).upper()
            comentario = re.search(r'Comentário:\s*(.*)', bloco, re.DOTALL).group(1).strip()
            texto_pergunta = re.sub(r'\nGabarito:.*', '', bloco, flags=re.DOTALL).strip()
            
            padrao_alternativas = r'([A-E])\)\s*(.*?)(?=\n[A-E]\)|\Z)'
            matches_alternativas = re.findall(padrao_alternativas, texto_pergunta, re.DOTALL)
            
            if matches_alternativas:
                modalidade = "ME"
                enunciado = re.search(r'\d+\.\s*(.*?)(?=\nA\))', texto_pergunta, re.DOTALL).group(1).strip()
                alternativas = {letra: texto.strip() for letra, texto in matches_alternativas}
            else:
                modalidade = "CE"
                enunciado = re.search(r'\d+\.\s*(.*)', texto_pergunta, re.DOTALL).group(1).strip()
                alternativas = None

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

    session.commit()
    session.close()
    print(f"✅ Sucesso! {questoes_inseridas} questões foram salvas no banco de dados.")

if __name__ == "__main__":
    processar_arquivo_txt(
        caminho_arquivo='questoes_brutas.txt',
        banca='Minha Revisão',
        ano=2026,
        id_assunto=1 
    )
