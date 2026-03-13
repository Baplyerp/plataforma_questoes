import streamlit as st
import re
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, Assunto
import sys
import os

# Esse comando diz ao Python: "Olhe também na pasta de cima!"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_schema import engine, Questao, HistoricoResolucao # Agora ele vai achar!

st.set_page_config(page_title="Importador", page_icon="📂")

def processar_texto(texto, id_assunto, banca, ano):
    padrao = r'(\d+\.\s+.*?Comentário:\s*.*?)(?=\n\n\d+\.|\Z)'
    blocos = re.findall(padrao, texto, re.DOTALL)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    contador = 0
    
    for bloco in blocos:
        try:
            gab = re.search(r'Gabarito:\s*([A-Ea-eCcEe])', bloco).group(1).upper()
            coment = re.search(r'Comentário:\s*(.*)', bloco, re.DOTALL).group(1).strip()
            # Simplificação do enunciado
            enunc = re.sub(r'\nGabarito:.*', '', bloco, flags=re.DOTALL).strip()
            
            nova_q = Questao(banca=banca, ano=ano, id_assunto=id_assunto, 
                             modalidade="CE" if len(gab) == 1 and gab in "CE" else "ME",
                             enunciado=enunc, gabarito=gab, comentario_teorico=coment)
            session.add(nova_q)
            contador += 1
        except: continue
        
    session.commit()
    session.close()
    return contador

st.title("📂 Importador Inteligente")
st.write("Cole o bloco de questões no formato padrão (Número. Enunciado -> Gabarito: X -> Comentário: ...)")

Session = sessionmaker(bind=engine)
session = Session()
assuntos = session.query(Assunto).all()
opcoes = {f"{a.nome}": a.id for a in assuntos}
session.close()

if opcoes:
    ass_id = st.selectbox("Assunto de Destino:", list(opcoes.keys()))
    banca = st.text_input("Banca:", value="Cebraspe")
    ano = st.number_input("Ano:", value=2026)
    texto_bruto = st.text_area("Cole as questões aqui:", height=300)
    
    if st.button("Processar e Salvar"):
        total = processar_texto(texto_bruto, opcoes[ass_id], banca, ano)
        st.success(f"{total} questões inseridas com sucesso!")
