import streamlit as st

st.set_page_config(
    page_title="Plataforma de Controle Interno",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Hub Central de Estudos - Gestão e Controle")
st.markdown("Bem-vindo à sua plataforma de alto rendimento.")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("🎯 **Foco da Semana:** Auditoria Governamental e LRF")
with col2:
    st.success("📈 **Último Simulado:** 85% de Acertos")
with col3:
    st.warning("⚠️ **Ponto de Atenção:** Revisar Receita Pública")

st.markdown("### 🚀 Próximos Passos")
st.write("Utilize o menu lateral para navegar entre a resolução de questões, a montagem dos seus cadernos específicos ou a análise profunda do seu desempenho.")
