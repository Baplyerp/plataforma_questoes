import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database_schema import engine, HistoricoResolucao, Questao, Assunto, Subtema, Disciplina

st.set_page_config(page_title="Meu Desempenho", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .dash-titulo { font-size: 2rem; font-weight: 800; color: #111827; }
    .dash-sub { font-size: 1.1rem; color: #4B5563; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="dash-titulo">📊 Centro de Telemetria e Análise</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Seus tempos de volta e performance por setor (Disciplina). Acompanhe sua evolução rumo à aprovação.</div>', unsafe_allow_html=True)

@st.cache_data(ttl=60) 
def extrair_dados_desempenho():
    Session = sessionmaker(bind=engine)
    session = Session()
    historico = session.query(HistoricoResolucao).all()
    
    dados = []
    for h in historico:
        q = h.questao
        disciplina_nome = q.assunto.subtema.disciplina.nome if q.assunto else "Sem Vínculo"
        
        dados.append({
            "Data": h.data_resolucao.date(),
            "Disciplina": disciplina_nome,
            "Modalidade": q.modalidade,
            "Acertou": 1 if h.acertou else 0,
            "Errou": 0 if h.acertou else 1
        })
    session.close()
    return pd.DataFrame(dados)

df = extrair_dados_desempenho()

if df.empty:
    st.info("🏁 Os boxes estão vazios! Você ainda não resolveu nenhuma questão no simulador principal. Vá para a pista e gere dados para a telemetria.")
else:
    total_resolvidas = len(df)
    total_acertos = df["Acertou"].sum()
    taxa_acerto = (total_acertos / total_resolvidas) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Volume de Treino (Total)", f"{total_resolvidas} questões")
    col2.metric("Acertos Absolutos", f"{total_acertos}")
    
    if taxa_acerto >= 80:
        col3.metric("Taxa de Conversão", f"{taxa_acerto:.1f}%", "Ritmo de Elite")
    elif taxa_acerto >= 65:
        col3.metric("Taxa de Conversão", f"{taxa_acerto:.1f}%", "Aviso: Zonas de frenagem perigosas", delta_color="off")
    else:
        col3.metric("Taxa de Conversão", f"{taxa_acerto:.1f}%", "Alerta Vermelho: Risco de DNF", delta_color="inverse")

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("🏁 Performance por Disciplina (Setores)")
        df_disc = df.groupby("Disciplina")["Acertou"].mean() * 100
        st.bar_chart(df_disc, color="#2563EB", height=300)
        st.caption("Eixo Y: Taxa de Acerto (%). Visualize qual matéria está atrasando o seu carro.")

    with colB:
        st.subheader("📈 Volume Diário (Evolução no Tempo)")
        df_tempo = df.groupby("Data").size()
        st.line_chart(df_tempo, color="#10B981", height=300)
        st.caption("Consistência é a chave. Mantenha a linha alta todos os dias.")

    st.markdown("---")
    st.subheader("⚖️ Raio-X das Modalidades")
    
    df_modalidade = df.groupby("Modalidade").agg(
        Total=("Acertou", "count"),
        Taxa_Acerto=("Acertou", lambda x: (x.mean() * 100).round(1))
    ).reset_index()

    df_modalidade["Modalidade"] = df_modalidade["Modalidade"].replace({"CE": "Lei Seca (Certo/Errado)", "ME": "Gerais (Múltipla Escolha)"})
    
    st.dataframe(df_modalidade, use_container_width=True, hide_index=True)
