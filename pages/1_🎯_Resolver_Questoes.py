import sys
import os
import streamlit as st

# =========================================================
# 1. GPS DE IMPORTAÇÃO (DEVE SER A PRIMEIRA COISA)
# =========================================================
# Movemos para o topo absoluto para o Python achar a raiz antes de qualquer import do banco
caminho_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if caminho_raiz not in sys.path:
    sys.path.append(caminho_raiz)

# Agora sim, com o caminho liberado, importamos o motor
try:
    from database_schema import engine, Questao, HistoricoResolucao, ConteudoTeorico
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    st.error(f"⚠️ Erro crítico de arquitetura: {e}")
    st.stop()

# =========================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Resolver Questões", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    .enunciado-box { background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 20px; border-radius: 5px; font-size: 1.1rem; line-height: 1.6; color: #2C3E50; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .metadados { font-size: 0.85rem; color: #7F8C8D; font-weight: bold; text-transform: uppercase; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 3. FUNÇÕES DE BANCO DE DADOS
# =========================================================
def buscar_dados():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # SQLAlchemy 2.0+ query style
        questoes = session.query(Questao).all()
        return questoes
    except Exception as e:
        st.error(f"❌ Erro na telemetria do banco: {e}")
        return []
    finally:
        session.close()

def salvar_resposta(id_q, resp, status):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        h = HistoricoResolucao(id_questao=id_q, resposta_marcada=resp, acertou=status)
        session.add(h)
        session.commit()
    finally:
        session.close()

# =========================================================
# 4. LÓGICA DE EXIBIÇÃO
# =========================================================

# Inicialização do estado
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'resp_confirmada' not in st.session_state: st.session_state.resp_confirmada = False

lista = buscar_dados()

st.title("🎯 Simulador de Questões")

if lista:
    q = lista[st.session_state.idx]
    
    st.markdown(f'<p class="metadados">{q.banca} {q.ano} • ID: {q.id}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="enunciado-box">{q.enunciado}</div>', unsafe_allow_html=True)

    # Escolha da modalidade
    if q.modalidade == "CE":
        escolha = st.radio("Julgamento:", ["Pendente", "Certo", "Errado"], horizontal=True, key=f"radio_{q.id}")
        final_resp = escolha[0] if escolha != "Pendente" else ""
    else:
        # Garante que alternativas existam para não quebrar a UI
        opts_list = [f"{k}) {v}" for k, v in q.alternativas.items()] if q.alternativas else []
        escolha = st.radio("Alternativas:", ["Pendente"] + opts_list, key=f"radio_{q.id}")
        final_resp = escolha[0] if escolha != "Pendente" else ""

    st.markdown("---")
    
    # Botão de confirmação
    if st.button("Confirmar Resposta", type="primary", disabled=st.session_state.resp_confirmada):
        if final_resp == "":
            st.warning("⚠️ Selecione uma opção antes de confirmar.")
        else:
            st.session_state.resp_confirmada = True
            salvar_resposta(q.id, final_resp, (final_resp == q.gabarito))
            st.rerun()

    # Feedback após responder
    if st.session_state.resp_confirmada:
        if final_resp == q.gabarito:
            st.success(f"✅ **Gabarito Correto!** Resposta: {q.gabarito}")
        else:
            st.error(f"❌ **Incorreto.** O gabarito oficial é: {q.gabarito}")
        
        if q.comentario_teorico:
            with st.expander("📝 Ver Comentário Estratégico", expanded=True):
                st.markdown(q.comentario_teorico, unsafe_allow_html=True)

    # Navegação entre questões
    st.divider()
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    
    with nav1:
        if st.button("⬅️ Anterior", use_container_width=True) and st.session_state.idx > 0:
            st.session_state.idx -= 1
            st.session_state.resp_confirmada = False
            st.rerun()
            
    with nav3:
        if st.button("Próxima ➡️", use_container_width=True) and st.session_state.idx < len(lista) - 1:
            st.session_state.idx += 1
            st.session_state.resp_confirmada = False
            st.rerun()
else:
    st.warning("🏁 O banco de dados está vazio. Vá para 'Gestão de Conteúdo' e adicione suas questões.")
