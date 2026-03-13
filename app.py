import streamlit as st

st.set_page_config(page_title="Plataforma de Controle", page_icon="🏛️", layout="wide")

st.title("🏛️ Hub Central de Estudos")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1: st.info("🎯 **Foco:** Auditoria e LRF")
with col2: st.success("📈 **Simulado:** 85% Acertos")
with col3: st.warning("⚠️ **Atenção:** Receita Pública")

st.write("Use o menu lateral para navegar.")
