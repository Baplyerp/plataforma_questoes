import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Edital, MateriaCiclo, SessaoEstudo

st.set_page_config(page_title="Zona de Estudo", page_icon="🧠", layout="wide")

# --- CSS PREMIUM (Adeus Planilhas) ---
st.markdown("""
    <style>
    .baply-header { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.5px; margin-bottom: 0px;}
    .baply-sub { font-size: 1.1rem; color: #6B7280; margin-bottom: 30px; }
    .card-materia { background-color: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-left: 8px solid; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;}
    .card-materia h3 { margin: 0; font-size: 1.2rem; color: #1F2937; }
    .card-materia p { margin: 0; color: #6B7280; font-size: 0.9rem; font-weight: 600; }
    .metodo-tag { background-color: #EEF2FF; color: #4338CA; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DO BANCO DE DADOS ---
def buscar_editais():
    Session = sessionmaker(bind=engine)
    session = Session()
    editais = session.query(Edital).all()
    # Expunge para podermos usar fora da sessão
    session.expunge_all()
    session.close()
    return editais

def criar_edital(nome, cargo, banca):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        novo = Edital(nome_concurso=nome, cargo=cargo, banca=banca)
        session.add(novo)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

def adicionar_materia(id_edital, nome_materia, peso, tempo_min, cor):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        nova = MateriaCiclo(id_edital=id_edital, nome=nome_materia, peso=peso, carga_horaria_meta_minutos=tempo_min, cor_hex=cor)
        session.add(nova)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

def buscar_materias_edital(id_edital):
    Session = sessionmaker(bind=engine)
    session = Session()
    materias = session.query(MateriaCiclo).filter_by(id_edital=id_edital).all()
    session.expunge_all()
    session.close()
    return materias

# --- INTERFACE VISUAL ---
st.markdown('<div class="baply-header">🧠 Central de Neuro-Estudos Baply</div>', unsafe_allow_html=True)
st.markdown('<div class="baply-sub">Configure seu edital alvo e monte seu ciclo de prática intercalada.</div>', unsafe_allow_html=True)

editais_db = buscar_editais()

tab1, tab2, tab3 = st.tabs(["🎯 1. Edital Alvo", "⚙️ 2. Montar Ciclo", "⏱️ 3. Modo Foco (Sessão)"])

# ==========================================
# ABA 1: CONFIGURAR EDITAL
# ==========================================
with tab1:
    col_ed1, col_ed2 = st.columns([1, 2])
    with col_ed1:
        st.markdown("### Novo Edital")
        with st.form("form_edital"):
            nome_ed = st.text_input("Concurso/Órgão", placeholder="Ex: Prefeitura de Catende")
            cargo_ed = st.text_input("Cargo Alvo", placeholder="Ex: Analista de Controle Interno")
            banca_ed = st.text_input("Banca Organizadora", placeholder="Ex: Cebraspe")
            submit_ed = st.form_submit_button("Cadastrar Alvo", use_container_width=True)
            
            if submit_ed and nome_ed and cargo_ed:
                if criar_edital(nome_ed, cargo_ed, banca_ed):
                    st.success("Alvo travado no sistema!")
                    st.rerun()

    with col_ed2:
        st.markdown("### Seus Projetos Atuais")
        if not editais_db:
            st.info("Nenhum edital cadastrado. Crie o seu primeiro projeto ao lado.")
        else:
            for ed in editais_db:
                status = "🟢 Ativo" if ed.ativo else "🔴 Pausado"
                st.markdown(f"""
                <div style="padding: 15px; border: 1px solid #E5E7EB; border-radius: 8px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #111827;">{ed.nome_concurso}</h4>
                    <p style="margin: 0; color: #4B5563;">Cargo: <b>{ed.cargo}</b> | Banca: {ed.banca or 'Não definida'}</p>
                    <span style="font-size: 0.8rem; font-weight: bold; color: #059669;">{status}</span>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# ABA 2: MONTAR O CICLO (A Mágica da Intercalação)
# ==========================================
with tab2:
    if not editais_db:
        st.warning("Cadastre um edital na aba anterior primeiro.")
    else:
        opcoes_editais = {f"{e.nome_concurso} - {e.cargo}": e.id for e in editais_db}
        edital_selecionado = st.selectbox("Selecione o Projeto para montar o ciclo:", list(opcoes_editais.keys()))
        id_ed_alvo = opcoes_editais[edital_selecionado]
        
        st.markdown("---")
        
        colM1, colM2 = st.columns([1, 2])
        
        with colM1:
            st.markdown("#### Adicionar Matéria ao Ciclo")
            with st.form("form_materia"):
                nome_mat = st.text_input("Disciplina", placeholder="Ex: Direito Administrativo")
                peso_mat = st.number_input("Peso no Edital", min_value=1, value=1)
                
                st.markdown("**Neuro-Alocação (Ritmo Ultradiano)**")
                tempo_mat = st.selectbox("Duração do Bloco", [
                    "90 min (Foco Profundo - Recomendado)", 
                    "60 min (Prática Intermediária)", 
                    "120 min (Imersão Máxima)",
                    "30 min (Revisão Rápida)"
                ])
                minutos_reais = int(tempo_mat.split(" ")[0])
                
                cor_mat = st.color_picker("Cor da Disciplina no Gráfico", "#3B82F6")
                
                add_mat = st.form_submit_button("Inserir no Ciclo 🔄", use_container_width=True)
                
                if add_mat and nome_mat:
                    if adicionar_materia(id_ed_alvo, nome_mat, peso_mat, minutos_reais, cor_mat):
                        st.success("Disciplina engatada no ciclo!")
                        st.rerun()

        with colM2:
            st.markdown("#### O Seu Ciclo de Prática Intercalada")
            materias_ciclo = buscar_materias_edital(id_ed_alvo)
            
            if not materias_ciclo:
                st.info("O ciclo deste edital está vazio. Adicione as matérias ao lado.")
            else:
                total_minutos = sum([m.carga_horaria_meta_minutos for m in materias_ciclo])
                horas_totais = total_minutos / 60
                st.caption(f"⏱️ Tempo total para girar o ciclo completo uma vez: **{horas_totais:.1f} horas**")
                
                for mat in materias_ciclo:
                    st.markdown(f"""
                    <div class="card-materia" style="border-left-color: {mat.cor_hex};">
                        <div>
                            <h3>{mat.nome}</h3>
                            <p>Peso: {mat.peso} | Meta: {mat.carga_horaria_meta_minutos} minutos</p>
                        </div>
                        <div class="metodo-tag">Bloco de {mat.carga_horaria_meta_minutos}m</div>
                    </div>
                    """, unsafe_allow_html=True)

# ==========================================
# ABA 3: MODO FOCO (Onde a mágica acontece)
# ==========================================
with tab3:
    st.markdown("### 🎧 Entrar na Zona de Foco")
    st.markdown("Aqui implementaremos o cronômetro inteligente que bloqueará distrações, medirá o seu tempo líquido de estudo e registrará a sua nota de foco (1 a 5) no banco de dados da Baply ao final da sessão. *(Módulo em construção pelas engenharias da Baply)*")
    
    st.info("💡 Como a neurociência prova, estudar por tempo líquido é mais importante do que estudar por horário fixo no relógio. A sua sessão de estudos será registrada na telemetria assim que você finalizar o bloco.")
    
    # Placeholder visual para o futuro timer
    st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #111827; border-radius: 20px; color: white; margin-top: 20px;">
            <h1 style="font-size: 5rem; margin: 0; color: #10B981;">00:00</h1>
            <p style="color: #9CA3AF; font-size: 1.2rem;">Selecione a matéria do ciclo para iniciar o cronômetro ultradiano.</p>
            <button style="background-color: #3B82F6; color: white; border: none; padding: 10px 30px; border-radius: 5px; font-size: 1.2rem; cursor: pointer; margin-top: 15px;">▶️ INICIAR SESSÃO</button>
        </div>
    """, unsafe_allow_html=True)
