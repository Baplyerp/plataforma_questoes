import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, HistoricoResolucao, ConteudoTeorico
import sys
import sys
import os

# Esse comando diz ao Python: "Olhe também na pasta de cima!"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_schema import engine, Questao, HistoricoResolucao # Agora ele vai achar!

st.set_page_config(page_title="Resolver Questões", page_icon="🎯", layout="wide")

# --- CSS PARA LIMPEZA VISUAL ---
st.markdown("""
    <style>
    .enunciado-box { background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 20px; border-radius: 5px; font-size: 1.1rem; line-height: 1.6; color: #2C3E50; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .metadados { font-size: 0.85rem; color: #7F8C8D; font-weight: bold; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

def buscar_dados():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Usamos o comando direto para evitar o erro de compatibilidade do Python 3.14
        questoes = session.query(Questao).all()
        return questoes
    except Exception as e:
        st.error(f"Erro ao buscar questões: {e}")
        return []
    finally:
        session.close()

def salvar_resposta(id_q, resp, status):
    Session = sessionmaker(bind=engine)
    session = Session()
    h = HistoricoResolucao(id_questao=id_q, resposta_marcada=resp, acertou=status)
    session.add(h)
    session.commit()
    session.close()

if 'idx' not in st.session_state: st.session_state.idx = 0
if 'resp' not in st.session_state: st.session_state.resp = False

lista = buscar_dados()

st.title("🎯 Simulador de Questões")

if lista:
    q = lista[st.session_state.idx]
    
    st.markdown(f'<p class="metadados">{q.banca} {q.ano} • ID:{q.id}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="enunciado-box">{q.enunciado}</div>', unsafe_allow_html=True)

    if q.modalidade == "CE":
        escolha = st.radio("Julgamento:", ["Pendente", "Certo", "Errado"], horizontal=True)
        final_resp = escolha[0] if escolha != "Pendente" else ""
    else:
        opts = [f"{k}) {v}" for k, v in q.alternativas.items()] if q.alternativas else []
        escolha = st.radio("Alternativas:", ["Pendente"] + opts)
        final_resp = escolha[0] if escolha != "Pendente" else ""

    if st.button("Confirmar Resposta", type="primary"):
        st.session_state.resp = True
        if final_resp != "":
            salvar_resposta(q.id, final_resp, (final_resp == q.gabarito))

    if st.session_state.resp:
        if final_resp == q.gabarito: st.success(f"✅ Correto! Gabarito: {q.gabarito}")
        else: st.error(f"❌ Errado. O gabarito é {q.gabarito}")
        if q.comentario_teorico:
            with st.expander("Ver Comentário"): st.markdown(q.comentario_teorico, unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Anterior") and st.session_state.idx > 0:
        st.session_state.idx -= 1
        st.session_state.resp = False
        st.rerun()
    if c2.button("Próxima ➡️") and st.session_state.idx < len(lista) - 1:
        st.session_state.idx += 1
        st.session_state.resp = False
        st.rerun()
else:
    st.warning("Nenhuma questão encontrada. Vá para Gestão de Conteúdo.")
