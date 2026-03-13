import streamlit as st
import random
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, Assunto

st.set_page_config(page_title="Telemetria Lei Seca", page_icon="🏎️", layout="wide")

# --- CSS: O VISUAL DA ESCUDERIA ---
st.markdown("""
    <style>
    .flashcard { background-color: #f8f9fa; border-left: 6px solid #2563EB; padding: 30px; border-radius: 8px; font-size: 1.3rem; line-height: 1.6; color: #1F2937; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
    .saldo-positivo { color: #10B981; font-size: 2.5rem; font-weight: 900; }
    .saldo-negativo { color: #EF4444; font-size: 2.5rem; font-weight: 900; }
    .saldo-neutro { color: #6B7280; font-size: 2.5rem; font-weight: 900; }
    .box-chefe { background-color: #111827; color: #F9FAFB; padding: 20px; border-radius: 8px; border-left: 5px solid #F59E0B; font-family: monospace; font-size: 1.1rem;}
    
    /* Classes de Feedback Animado F1 */
    .f1-acerto { background-color: #D1FAE5; padding: 15px; border-radius: 10px; border-left: 8px solid #10B981; margin-bottom: 15px;}
    .f1-erro { background-color: #FEE2E2; padding: 15px; border-radius: 10px; border-left: 8px solid #EF4444; margin-bottom: 15px;}
    .f1-branco { background-color: #FEF3C7; padding: 15px; border-radius: 10px; border-left: 8px solid #F59E0B; margin-bottom: 15px;}
    .f1-titulo { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
    .f1-animacao { font-size: 3rem; margin-top: 5px; }
    
    /* Pódio Customizado */
    .podio-card { text-align: center; padding: 20px; border-radius: 15px; margin-top: 20px; color: white; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);}
    .podio-ouro { background: linear-gradient(135deg, #F59E0B, #D97706); }
    .podio-prata { background: linear-gradient(135deg, #9CA3AF, #6B7280); }
    .podio-bronze { background: linear-gradient(135deg, #B45309, #78350F); }
    .podio-dnf { background: linear-gradient(135deg, #EF4444, #991B1B); }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM O BANCO (BLINDADA) ---
def buscar_filtros_disponiveis():
    Session = sessionmaker(bind=engine)
    session = Session()
    assuntos = session.query(Assunto).join(Questao).filter(Questao.modalidade == "CE").distinct().all()
    opcoes = {f"[{a.subtema.disciplina.nome}] {a.subtema.nome} ➡️ {a.nome}": a.id for a in assuntos}
    session.close()
    return opcoes

def buscar_questoes_por_assunto(id_assunto):
    Session = sessionmaker(bind=engine)
    session = Session()
    questoes = session.query(Questao).filter(Questao.modalidade == "CE", Questao.id_assunto == id_assunto).all()
    session.close()
    return questoes

# --- MEMÓRIA DO PILOTO ---
if 'ls_estado' not in st.session_state: st.session_state.ls_estado = "GARAGEM"
if 'ls_questoes' not in st.session_state: st.session_state.ls_questoes = []
if 'ls_indice' not in st.session_state: st.session_state.ls_indice = 0
if 'ls_acertos' not in st.session_state: st.session_state.ls_acertos = 0
if 'ls_erros' not in st.session_state: st.session_state.ls_erros = 0
if 'ls_brancos' not in st.session_state: st.session_state.ls_brancos = 0
if 'ls_respondido' not in st.session_state: st.session_state.ls_respondido = False
if 'ls_escolha' not in st.session_state: st.session_state.ls_escolha = None

# --- FUNÇÕES DO MOTOR ---
def iniciar_corrida(id_assunto):
    st.session_state.ls_questoes = buscar_questoes_por_assunto(id_assunto)
    random.shuffle(st.session_state.ls_questoes) # Mistura as questões para o treino não ficar viciado!
    st.session_state.ls_estado = "PISTA"
    st.session_state.ls_indice = 0
    st.session_state.ls_acertos = 0
    st.session_state.ls_erros = 0
    st.session_state.ls_brancos = 0
    st.session_state.ls_respondido = False
    st.session_state.ls_escolha = None

def registrar_resposta(escolha):
    st.session_state.ls_respondido = True
    st.session_state.ls_escolha = escolha
    gabarito = st.session_state.ls_questoes[st.session_state.ls_indice].gabarito
    
    if escolha == "Branco": st.session_state.ls_brancos += 1
    elif escolha == gabarito: st.session_state.ls_acertos += 1
    else: st.session_state.ls_erros += 1

def proxima_curva():
    st.session_state.ls_indice += 1
    st.session_state.ls_respondido = False
    st.session_state.ls_escolha = None
    if st.session_state.ls_indice >= len(st.session_state.ls_questoes):
        st.session_state.ls_estado = "BOX"

def voltar_garagem():
    st.session_state.ls_estado = "GARAGEM"

# ==========================================
# TELA 1: A GARAGEM
# ==========================================
if st.session_state.ls_estado == "GARAGEM":
    st.title("🏎️ Garagem de Alta Performance")
    st.markdown("Selecione o pneu, o mapeamento do motor e o bloco de leis que vamos atacar agora.")
    st.markdown("---")
    opcoes = buscar_filtros_disponiveis()
    if not opcoes:
        st.warning("⚠️ O seu carro está sem combustível. Adicione questões CE na Gestão de Conteúdo.")
    else:
        alvo = st.selectbox("🎯 Alvo de Domínio (Artigos/Lei):", list(opcoes.keys()))
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🟢 LIGAR OS MOTORES (Iniciar Treino)", type="primary", use_container_width=True):
            iniciar_corrida(opcoes[alvo])
            st.rerun()

# ==========================================
# TELA 2: A PISTA (Flashcards Cebraspe)
# ==========================================
elif st.session_state.ls_estado == "PISTA":
    q_atual = st.session_state.ls_questoes[st.session_state.ls_indice]
    total_q = len(st.session_state.ls_questoes)
    saldo_liquido = st.session_state.ls_acertos - st.session_state.ls_erros

    with st.sidebar:
        st.header("⏱️ Telemetria")
        cor_saldo = "saldo-positivo" if saldo_liquido > 0 else "saldo-negativo" if saldo_liquido < 0 else "saldo-neutro"
        st.markdown(f"**Pontuação Líquida:** <br><span class='{cor_saldo}'>{saldo_liquido} pts</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.metric("🟩 Acertos (+1)", st.session_state.ls_acertos)
        st.metric("🟥 Erros (-1)", st.session_state.ls_erros)
        st.metric("⬜ Em Branco (0)", st.session_state.ls_brancos)
        st.markdown("---")
        if st.button("🛑 Abortar Volta (Voltar)", use_container_width=True):
            voltar_garagem()
            st.rerun()

    st.progress(st.session_state.ls_indice / total_q, text=f"Curva {st.session_state.ls_indice + 1} de {total_q}")
    st.markdown(f'<div class="flashcard">{q_atual.enunciado}</div>', unsafe_allow_html=True)

    if not st.session_state.ls_respondido:
        col1, col2, col3 = st.columns(3)
        with col1: st.button("🟩 CERTO", use_container_width=True, on_click=registrar_resposta, args=("C",))
        with col2: st.button("🟥 ERRADO", use_container_width=True, on_click=registrar_resposta, args=("E",))
        with col3: st.button("⬜ DEIXAR EM BRANCO", use_container_width=True, on_click=registrar_resposta, args=("Branco",))
    else:
        escolha = st.session_state.ls_escolha
        gabarito = q_atual.gabarito
        
        frases_acerto = [
            "DRS Aberto! Ultrapassagem perfeita na pegadinha da banca.",
            "Volta mais rápida da sessão! Gabarito cravado.",
            "Piloto de elite! Passou ileso pela armadilha do examinador.",
            "Traçado perfeito! Você engoliu essa lei seca."
        ]
        frases_erro = [
            "Ihh! Travou os freios e passou reto na curva. Bora revisar!",
            "Toque no muro! A banca foi mais rápida dessa vez.",
            "Rodou na pista! Faltou aderência na leitura dessa lei.",
            "Bandeira amarela! Essa pegadinha furou o seu pneu."
        ]
        frases_branco = [
            "Safety Car na pista! Decisão inteligente para proteger a pontuação.",
            "Recolheu para o box. Melhor não pontuar do que bater o carro!",
            "Estratégia conservadora e calculista. Preservou o motor para a próxima."
        ]
        
        # O Motor foi consertado! direction="left" faz o carro ir para a frente!
        if escolha == "Branco":
            st.markdown(f"""
                <div class="f1-branco">
                    <div class="f1-titulo">🟡 {random.choice(frases_branco)}</div>
                    <div style="color: #92400E;">O gabarito oficial era: <b>{gabarito}</b>. Ninguém perdeu pontos.</div>
                    <marquee direction="left" scrollamount="15" class="f1-animacao">🟡🟡🚓</marquee>
                </div>
            """, unsafe_allow_html=True)
            
        elif escolha == gabarito:
            st.markdown(f"""
                <div class="f1-acerto">
                    <div class="f1-titulo">🟢 {random.choice(frases_acerto)}</div>
                    <div style="color: #065F46;">Você marcou {escolha} e ganhou <b>+1 ponto!</b></div>
                    <marquee direction="left" scrollamount="35" class="f1-animacao">💨💨💨🏎️</marquee>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
                <div class="f1-erro">
                    <div class="f1-titulo">🔴 {random.choice(frases_erro)}</div>
                    <div style="color: #991B1B;">Você marcou {escolha}, mas o gabarito é <b>{gabarito}</b>. Perdeu <b>-1 ponto</b>.</div>
                    <marquee direction="left" scrollamount="10" class="f1-animacao">💥🏎️💥</marquee>
                </div>
            """, unsafe_allow_html=True)

        if q_atual.comentario_teorico:
            st.markdown(q_atual.comentario_teorico, unsafe_allow_html=True) 
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Acelerar para a Próxima Curva ➡️", type="primary", use_container_width=True, on_click=proxima_curva)

# ==========================================
# TELA 3: O BOX (Pódio e Classificação Cebraspe)
# ==========================================
elif st.session_state.ls_estado == "BOX":
    st.title("🏁 Fim da Sessão de Treino")
    total_q = len(st.session_state.ls_questoes)
    saldo_final = st.session_state.ls_acertos - st.session_state.ls_erros
    
    # Cálculo real do Cebraspe: Saldo Líquido / Total de Questões
    aproveitamento = (saldo_final / total_q) * 100 if total_q > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alvos Úteis", total_q)
    col2.metric("Acertos", st.session_state.ls_acertos)
    col3.metric("Erros Fatais", st.session_state.ls_erros)
    col4.metric("Saldo Líquido", saldo_final)

    st.markdown("---")
    
    # A LÓGICA DO PÓDIO (Régua Alta)
    if aproveitamento >= 90:
        st.balloons()
        st.markdown(f"""
        <div class="podio-card podio-ouro">
            <h1 style="font-size: 4rem; margin: 0;">🏆 P1</h1>
            <h2>Nível: Piloto Campeão Mundial (Lenda)</h2>
            <p style="font-size: 1.2rem;"><b>Aproveitamento Líquido: {aproveitamento:.1f}%</b></p>
            <p>Impecável! Você está destruindo a banca. Dominou a letra da lei, desviou de todas as pegadinhas e teve a frieza de um campeão. A sua aprovação na área de Controle é questão de tempo.</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif aproveitamento >= 82:
        st.markdown(f"""
        <div class="podio-card podio-prata">
            <h1 style="font-size: 4rem; margin: 0;">🥈 P2</h1>
            <h2>Nível: Piloto de Elite (No Pódio)</h2>
            <p style="font-size: 1.2rem;"><b>Aproveitamento Líquido: {aproveitamento:.1f}%</b></p>
            <p>Excelente corrida! Você está no pódio e com nota suficiente para passar dentro das vagas de quase qualquer Tribunal de Contas do país. Ajuste só mais alguns milésimos de segundo nos resumos e o ouro será seu.</p>
        </div>
        """, unsafe_allow_html=True)

    elif aproveitamento >= 75:
        st.markdown(f"""
        <div class="podio-card podio-bronze">
            <h1 style="font-size: 4rem; margin: 0;">🥉 P3</h1>
            <h2>Nível: Piloto Promissor (Zona de Pontuação)</h2>
            <p style="font-size: 1.2rem;"><b>Aproveitamento Líquido: {aproveitamento:.1f}%</b></p>
            <p>Você sobreviveu à linha de corte do Cebraspe e pontuou! Mas cuidado, a nota de corte está subindo e você está no limite da aderência. Se tivesse chutado uma questão a mais, estaria desclassificado.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="podio-card podio-dnf">
            <h1 style="font-size: 4rem; margin: 0;">💀 DNF</h1>
            <h2>Nível: Piloto de Testes (Desclassificado)</h2>
            <p style="font-size: 1.2rem;"><b>Aproveitamento Líquido: {aproveitamento:.1f}%</b></p>
            <p>Bandeira Vermelha. Seu carro quebrou (Did Not Finish). No Cebraspe, fazer menos de 75% líquido para a área de Controle é ficar de fora da lista. Você perdeu pontos preciosos por chutar sem ter certeza. Volte para a base teórica imediatamente!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Voltar para a Garagem", type="primary", use_container_width=True):
        voltar_garagem()
        st.rerun()