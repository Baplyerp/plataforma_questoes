import streamlit as st
from streamlit_quill import st_quill
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, Assunto, Subtema, Disciplina
import sys
import os

# Esse comando diz ao Python: "Olhe também na pasta de cima!"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_schema import engine, Questao, HistoricoResolucao # Agora ele vai achar!

st.set_page_config(page_title="Gestão", page_icon="⚙️")

def get_pastas():
    Session = sessionmaker(bind=engine)
    session = Session()
    dados = session.query(Assunto).all()
    opcoes = {f"[{a.subtema.disciplina.nome}] {a.nome}": a.id for a in dados}
    session.close()
    return opcoes

st.title("⚙️ Gestão de Conteúdo")
pastas = get_pastas()

with st.expander("➕ Criar Nova Disciplina/Assunto"):
    d = st.text_input("Disciplina")
    s = st.text_input("Subtema")
    a = st.text_input("Assunto")
    if st.button("Salvar Pasta"):
        Session = sessionmaker(bind=engine)
        session = Session()
        # Lógica simplificada de inserção
        new_d = Disciplina(nome=d); session.add(new_d); session.flush()
        new_s = Subtema(nome=s, id_disciplina=new_d.id); session.add(new_s); session.flush()
        new_a = Assunto(nome=a, id_subtema=new_s.id); session.add(new_a)
        session.commit(); session.close()
        st.success("Pasta Criada!"); st.rerun()

with st.expander("📝 Cadastrar Questão"):
    if pastas:
        p_id = st.selectbox("Pasta:", list(pastas.keys()))
        banca = st.text_input("Banca")
        ano = st.number_input("Ano", value=2026)
        mod = st.selectbox("Tipo", ["CE", "ME"])
        enunc = st_quill(placeholder="Enunciado...")
        gab = st.text_input("Gabarito (C, E ou A, B, C...)")
        if st.button("Injetar Questão"):
            Session = sessionmaker(bind=engine)
            session = Session()
            q = Questao(banca=banca, ano=ano, id_assunto=pastas[p_id], modalidade=mod, enunciado=enunc, gabarito=gab.upper())
            session.add(q); session.commit(); session.close()
            st.success("Questão Salva!")
