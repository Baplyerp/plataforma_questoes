import streamlit as st
import random
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao

st.set_page_config(page_title="Lei Seca", page_icon="🏎️")

def get_ce_questoes():
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(Questao).filter_by(modalidade="CE").all()
    session.close()
    return q

st.title("🏎️ Treino de Lei Seca (C/E)")

if 'pool' not in st.session_state: 
    st.session_state.pool = get_ce_questoes()
    random.shuffle(st.session_state.pool)

if st.session_state.pool:
    curr = st.session_state.pool[0]
    st.info(curr.enunciado)
    
    col1, col2 = st.columns(2)
    if col1.button("✅ CERTO"):
        if curr.gabarito == "C": st.balloons()
        else: st.error("Era Errado!")
    if col2.button("❌ ERRADO"):
        if curr.gabarito == "E": st.balloons()
        else: st.error("Era Certo!")
    
    if st.button("Próxima Lei ➡️"):
        st.session_state.pool.pop(0)
        st.rerun()
else:
    st.success("Fim do treino!")
    if st.button("Recarregar"): 
        st.session_state.pool = get_ce_questoes()
        st.rerun()
