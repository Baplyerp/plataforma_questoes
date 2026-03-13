import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, HistoricoResolucao, ConteudoTeorico

st.set_page_config(page_title="Resolver Questões", page_icon="🎯", layout="wide")

# --- CUSTOMIZAÇÃO VISUAL (CSS PREMIUM) ---
st.markdown("""
    <style>
    /* Estilo limpo e focado para o enunciado da questão */
    .enunciado-box {
        background-color: #FFFFFF;
        border-left: 5px solid #1E3A8A; /* Barra lateral azul elegante */
        padding: 20px 25px;
        border-radius: 5px;
        font-size: 1.15rem;
        line-height: 1.6;
        color: #2C3E50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        margin-top: 10px;
    }
    .metadados-questao {
        font-size: 0.9rem;
        color: #7F8C8D;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O BANCO ---
def buscar_todas_questoes():
    Session = sessionmaker(bind=engine)
    session = Session()
    questoes = session.query(Questao).all()
    session.close()
    return questoes

def buscar_teoria_vinculada(id_conteudo):
    Session = sessionmaker(bind=engine)
    session = Session()
    teoria = session.query(ConteudoTeorico).filter_by(id=id_conteudo).first()
    session.close()
    return teoria

def salvar_resposta_no_banco(id_questao, resposta_marcada, acertou):
    Session = sessionmaker(bind=engine)
    session = Session()
    novo_historico = HistoricoResolucao(
        id_questao=id_questao, resposta_marcada=resposta_marcada, acertou=acertou
    )
    session.add(novo_historico)
    session.commit()
    session.close()

# --- MEMÓRIA DA SESSÃO ---
if 'indice_atual' not in st.session_state:
    st.session_state.indice_atual = 0
if 'respondido' not in st.session_state:
    st.session_state.respondido = False

questoes_totais = buscar_todas_questoes()

# --- INTERFACE PRINCIPAL ---
st.title("🎯 Resolução de Questões")
st.markdown("---")

if len(questoes_totais) > 0:
    questao_atual = questoes_totais[st.session_state.indice_atual]
    
    col_principal, col_lateral = st.columns([3, 1])
    
    with col_principal:
        # Cronômetro em JavaScript (Roda liso sem travar o Python)
        if not st.session_state.respondido:
            components.html("""
                <div style="font-family: sans-serif; font-size: 1.1rem; font-weight: bold; color: #E67E22; text-align: right;">
                    ⏱️ <span id="time">00:00</span>
                </div>
                <script>
                    var sec = 0;
                    setInterval(function(){
                        sec++;
                        var m = Math.floor(sec/60).toString().padStart(2,'0');
                        var s = (sec%60).toString().padStart(2,'0');
                        document.getElementById("time").innerHTML = m + ":" + s;
                    }, 1000);
                </script>
            """, height=30)
        
        # Cabeçalho da Questão (Metadados)
        st.markdown(f'<p class="metadados-questao">Q{questao_atual.id} • {questao_atual.banca} • {questao_atual.ano} • {questao_atual.nivel or "Nível Não Informado"}</p>', unsafe_allow_html=True)
        
        # O Novo Enunciado Limpo
        st.markdown(f'<div class="enunciado-box">{questao_atual.enunciado}</div>', unsafe_allow_html=True)
        
        # --- ÁREA DE RESPOSTA ---
        if questao_atual.modalidade == "CE":
            resposta = st.radio("Julgue o item:", ["Selecione...", "Certo", "Errado"], key=f"rad_{questao_atual.id}")
            resposta_formatada = resposta[0] if resposta != "Selecione..." else ""
            
        elif questao_atual.modalidade == "ME":
            opcoes = ["Selecione..."]
            for letra, texto in questao_atual.alternativas.items():
                opcoes.append(f"{letra}) {texto}")
            resposta = st.radio("Escolha a alternativa:", opcoes, key=f"rad_{questao_atual.id}")
            resposta_formatada = resposta.split(")")[0] if resposta != "Selecione..." else ""
            
        # Botão de Responder
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Responder", type="primary"):
            st.session_state.respondido = True
            if resposta_formatada != "":
                 acertou_questao = (resposta_formatada == questao_atual.gabarito)
                 salvar_resposta_no_banco(questao_atual.id, resposta_formatada, acertou_questao)
        
        # --- FEEDBACK E COMENTÁRIOS ---
        if st.session_state.respondido:
            st.markdown("---")
            if resposta_formatada == questao_atual.gabarito:
                st.success("✅ **Gabarito Correto!** Excelente análise.")
            elif resposta != "Selecione...":
                st.error(f"❌ **Incorreto.** O gabarito oficial é a letra **{questao_atual.gabarito}**.")
            else:
                st.warning("Selecione uma alternativa antes de responder.")
                
            # Mostra o comentário estratégico se existir
            if questao_atual.comentario_teorico:
                with st.expander("🔥 Comentário Estratégico", expanded=True):
                    st.markdown(questao_atual.comentario_teorico, unsafe_allow_html=True)
            
            # VÍNCULO TEÓRICO (A Mágica da Interoperabilidade)
            if questao_atual.id_conteudo:
                teoria = buscar_teoria_vinculada(questao_atual.id_conteudo)
                if teoria:
                    with st.expander(f"📚 Ver Base Teórica: {teoria.titulo}", expanded=False):
                        if teoria.url_video:
                            st.video(teoria.url_video)
                        st.markdown(teoria.texto_rico, unsafe_allow_html=True)
            else:
                st.caption("⚠️ Esta questão ainda não possui um resumo teórico vinculado.")
        
        st.markdown("---")
        
        # Navegação
        col_nav1, col_nav2, col_nav3 = st.columns(3)
        with col_nav1:
            if st.button("⬅️ Anterior") and st.session_state.indice_atual > 0:
                st.session_state.indice_atual -= 1
                st.session_state.respondido = False
                st.rerun()
        with col_nav3:
            if st.button("Próxima ➡️") and st.session_state.indice_atual < len(questoes_totais) - 1:
                st.session_state.indice_atual += 1
                st.session_state.respondido = False
                st.rerun()

    with col_lateral:
        st.subheader("Painel de Bordo")
        st.metric(label="Questões no Banco", value=len(questoes_totais))
        st.progress((st.session_state.indice_atual + 1) / len(questoes_totais), text=f"Progresso: {st.session_state.indice_atual + 1} de {len(questoes_totais)}")
else:
    st.info("O seu banco de dados está zerado. Vá em 'Gestão de Conteúdo' e adicione suas primeiras questões para iniciar o simulador!")