import streamlit as st
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Edital, MateriaCiclo, SessaoEstudo
import datetime

st.set_page_config(page_title="Zona de Estudo", page_icon="🧠", layout="wide")

def buscar_editais():
    Session = sessionmaker(bind=engine)
    session = Session()
    editais = session.query(Edital).all()
    session.close()
    return editais

def salvar_sessao(id_materia, duracao, foco):
    Session = sessionmaker(bind=engine)
    session = Session()
    sessao = SessaoEstudo(id_materia=id_materia, duracao_minutos=duracao, foco_rating=foco)
    session.add(sessao)
    session.commit()
    session.close()

st.title("🧠 Zona de Estudo (Neurociência Aplicada)")
st.markdown("Gerencie seu ciclo de estudos com base na técnica de **Intercalação de Matérias**.")

editais = buscar_editais()

if not editais:
    st.warning("Nenhum edital cadastrado. Vá em 'Gestão' ou use o terminal.")
else:
    edital_ref = st.selectbox("Selecione o Edital Alvo:", editais, format_func=lambda x: f"{x.nome_concurso} - {x.cargo}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⏱️ Registrar Sessão de Estudo")
        with st.form("form_estudo"):
            materias = edital_ref.materias
            if materias:
                m_sel = st.selectbox("Matéria do Ciclo:", materias, format_func=lambda x: x.nome)
                duracao = st.slider("Duração (Minutos):", 15, 240, 60)
                foco = st.select_slider("Nível de Foco/Retenção:", options=[1, 2, 3, 4, 5])
                if st.form_submit_button("Finalizar e Registrar"):
                    salvar_sessao(m_sel.id, duracao, foco)
                    st.success("Sessão salva! O cérebro agradece a consistência.")
            else:
                st.info("Cadastre as matérias deste edital no banco.")

    with col2:
        st.subheader("📊 Status do Ciclo")
        # Aqui no futuro entra o gráfico de pizza com o tempo gasto vs meta
        st.caption("A neurociência sugere blocos de 50min com 10min de pausa para maximizar a memória de longo prazo.")
