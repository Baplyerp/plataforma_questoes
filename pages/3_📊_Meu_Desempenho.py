import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database_schema import engine, HistoricoResolucao
import sys
import os

# Esse comando diz ao Python: "Olhe também na pasta de cima!"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_schema import engine, Questao, HistoricoResolucao # Agora ele vai achar!

st.set_page_config(page_title="Desempenho", page_icon="📊")

def carregar_stats():
    Session = sessionmaker(bind=engine)
    session = Session()
    h = session.query(HistoricoResolucao).all()
    session.close()
    return pd.DataFrame([{"Acertou": x.acertou, "Data": x.data_resolucao} for x in h])

st.title("📊 Telemetria de Desempenho")
df = carregar_stats()

if not df.empty:
    acertos = df["Acertou"].sum()
    total = len(df)
    taxa = (acertos/total)*100
    
    c1, c2 = st.columns(2)
    c1.metric("Total Resolvidas", total)
    c2.metric("Taxa de Acerto", f"{taxa:.1f}%")
    
    st.line_chart(df.groupby(df['Data'].dt.date).count()['Acertou'])
else:
    st.info("Ainda não há dados de resolução.")
