import streamlit as st
from streamlit_quill import st_quill
from sqlalchemy.orm import sessionmaker
from database_schema import engine, Questao, Assunto, Subtema, Disciplina, ConteudoTeorico

st.set_page_config(page_title="Gestão de Conteúdo", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .titulo-secao { font-size: 1.5rem; font-weight: 600; color: #1E3A8A; margin-bottom: 0px; }
    .subtexto { font-size: 0.9rem; color: #6B7280; margin-bottom: 20px; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.15rem; font-weight: bold; color: #374151; }
    </style>
""", unsafe_allow_html=True)

def buscar_pastas_formatadas():
    Session = sessionmaker(bind=engine)
    session = Session()
    assuntos = session.query(Assunto).all()
    opcoes = {f"[{a.subtema.disciplina.nome}] {a.subtema.nome} ➡️ {a.nome}": a.id for a in assuntos}
    session.close()
    return opcoes

def buscar_dados_para_edicao(id_assunto):
    Session = sessionmaker(bind=engine)
    session = Session()
    a = session.query(Assunto).get(id_assunto)
    dados = (a.subtema.disciplina.nome, a.subtema.nome, a.nome) if a else ("", "", "")
    session.close()
    return dados

def criar_nova_pasta(nome_disc, nome_sub, nome_assunto):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        disc = session.query(Disciplina).filter_by(nome=nome_disc).first()
        if not disc:
            disc = Disciplina(nome=nome_disc)
            session.add(disc)
            session.flush()
        sub = session.query(Subtema).filter_by(nome=nome_sub, id_disciplina=disc.id).first()
        if not sub:
            sub = Subtema(nome=nome_sub, id_disciplina=disc.id)
            session.add(sub)
            session.flush()
        ass = session.query(Assunto).filter_by(nome=nome_assunto, id_subtema=sub.id).first()
        if not ass:
            ass = Assunto(nome=nome_assunto, id_subtema=sub.id)
            session.add(ass)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

def editar_pasta(id_assunto, novo_disc, novo_sub, novo_assunto):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        a = session.query(Assunto).get(id_assunto)
        if a:
            a.nome = novo_assunto
            a.subtema.nome = novo_sub
            a.subtema.disciplina.nome = novo_disc
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

def buscar_teorias_por_assunto(id_assunto):
    Session = sessionmaker(bind=engine)
    session = Session()
    teorias = session.query(ConteudoTeorico).filter_by(id_assunto=id_assunto).all()
    opcoes = {"Nenhum (Questão avulsa nesta pasta)": None}
    for t in teorias: opcoes[t.titulo] = t.id
    session.close()
    return opcoes

def salvar_teoria_direta(id_assunto, titulo, url_video, texto):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        nova_teoria = ConteudoTeorico(id_assunto=id_assunto, titulo=titulo, url_video=url_video, texto_rico=texto)
        session.add(nova_teoria)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

def salvar_questao(banca, ano, id_assunto, id_conteudo, modalidade, enunciado, alternativas, gabarito, comentario):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        nova_questao = Questao(
            banca=banca, ano=ano, id_assunto=id_assunto, id_conteudo=id_conteudo,
            modalidade=modalidade, enunciado=enunciado, alternativas=alternativas,
            gabarito=gabarito, comentario_teorico=comentario
        )
        session.add(nova_questao)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

def buscar_questoes_por_filtro(id_assunto, modalidade):
    Session = sessionmaker(bind=engine)
    session = Session()
    questoes = session.query(Questao).filter_by(id_assunto=id_assunto, modalidade=modalidade).all()
    opcoes = {f"ID {q.id} | {q.banca} {q.ano}": q for q in questoes}
    session.expunge_all() 
    session.close()
    return opcoes

def atualizar_questao(id_questao, banca, ano, gabarito, enunciado, alternativas, comentario):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        q = session.query(Questao).get(id_questao)
        if q:
            q.banca = banca
            q.ano = ano
            q.gabarito = gabarito
            q.enunciado = enunciado
            q.alternativas = alternativas 
            q.comentario_teorico = comentario
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

st.markdown('<p class="titulo-secao">⚙️ Linha de Montagem de Conteúdo</p>', unsafe_allow_html=True)
st.markdown('<p class="subtexto">Crie, edite e alimente suas pastas de organização. O sistema cuidará da telemetria de forma automática.</p>', unsafe_allow_html=True)

opcoes_pastas = buscar_pastas_formatadas()

with st.expander("📁 ETAPA 1: Gerenciar Pastas (Disciplina e Assunto)", expanded=False):
    tab1, tab2 = st.tabs(["➕ Criar Nova Pasta", "✏️ Editar Pasta Existente"])
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1: nova_disc = st.text_input("1. Disciplina", key="new_d")
        with col2: novo_sub = st.text_input("2. Subtema", key="new_s")
        with col3: novo_assunto = st.text_input("3. Assunto", key="new_a")
        if st.button("Criar Pasta", type="secondary"):
            if nova_disc and novo_sub and novo_assunto:
                if criar_nova_pasta(nova_disc, novo_sub, novo_assunto):
                    st.success("✅ Pasta criada!")
                    st.rerun()
    with tab2:
        if opcoes_pastas:
            pasta_editar = st.selectbox("Selecione a Pasta para Correção:", list(opcoes_pastas.keys()), key="edit_sel")
            id_editar = opcoes_pastas[pasta_editar]
            atual_d, atual_s, atual_a = buscar_dados_para_edicao(id_editar)
            colE1, colE2, colE3 = st.columns(3)
            with colE1: edit_disc = st.text_input("Disciplina", value=atual_d, key="ed_d")
            with colE2: edit_sub = st.text_input("Subtema", value=atual_s, key="ed_s")
            with colE3: edit_ass = st.text_input("Assunto", value=atual_a, key="ed_a")
            if st.button("💾 Salvar Correções", type="primary"):
                if editar_pasta(id_editar, edit_disc, edit_sub, edit_ass):
                    st.success("Nomes atualizados!")
                    st.rerun()

with st.expander("📖 ETAPA 2: Adicionar Resumo ou Súmulas à Pasta", expanded=False):
    if opcoes_pastas:
        pasta_selecionada = st.selectbox("Escolha a Pasta de Destino:", list(opcoes_pastas.keys()), key="sel_pasta_teoria")
        id_pasta_teoria = opcoes_pastas[pasta_selecionada]
        colT1, colT2 = st.columns([2, 1])
        with colT1: titulo_teoria = st.text_input("Título do Material", key="tit_t")
        with colT2: video_teoria = st.text_input("Link YouTube", key="vid_t")
        texto_teoria = st_quill(placeholder="Cole a lei seca ou resumos...", key="quill_teoria")
        if st.button("Salvar Teoria", type="secondary"):
            if titulo_teoria and texto_teoria:
                if salvar_teoria_direta(id_pasta_teoria, titulo_teoria, video_teoria, texto_teoria):
                    st.success("Teoria salva!")
                    st.rerun()

with st.expander("🎯 ETAPA 3: Cadastrar Nova Questão", expanded=False):
    if opcoes_pastas:
        pasta_q_selecionada = st.selectbox("1. Em qual pasta esta questão vai ficar?", list(opcoes_pastas.keys()), key="sel_pasta_q")
        id_pasta_q = opcoes_pastas[pasta_q_selecionada]
        opcoes_vinculo = buscar_teorias_por_assunto(id_pasta_q)
        vinculo_teorico = st.selectbox("2. Vincular a algum resumo?", list(opcoes_vinculo.keys()))
        id_vinculo_q = opcoes_vinculo[vinculo_teorico]
        colQ1, colQ2, colQ3 = st.columns([1, 1, 2])
        with colQ1: banca_q = st.text_input("Banca", key="bq")
        with colQ2: ano_q = st.number_input("Ano", value=2026, step=1, key="aq")
        with colQ3: mod_q = st.selectbox("Modalidade", ["Certo/Errado (CE)", "Múltipla Escolha (ME)"])
        enunciado_q = st_quill(placeholder="Enunciado...", key="q_enunciado_new")
        alternativas_dict = None
        if mod_q == "Múltipla Escolha (ME)":
            colA, colB = st.columns(2)
            with colA: alt_a = st.text_input("A)")
            with colA: alt_b = st.text_input("B)")
            with colA: alt_c = st.text_input("C)")
            with colB: alt_d = st.text_input("D)")
            with colB: alt_e = st.text_input("E)")
            alternativas_dict = {"A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e}
            gabarito_q = st.selectbox("Gabarito", ["A", "B", "C", "D", "E"], key="gab_me")
        else:
            gabarito_q = st.selectbox("Gabarito", ["C", "E"], key="gab_ce")
        comentario_q = st_quill(placeholder="Comentário...", key="q_coment_new")
        if st.button("🚀 INJETAR QUESTÃO NO SISTEMA", type="primary"):
            if banca_q and enunciado_q:
                sigla = "CE" if mod_q == "Certo/Errado (CE)" else "ME"
                if salvar_questao(banca_q, ano_q, id_pasta_q, id_vinculo_q, sigla, enunciado_q, alternativas_dict, gabarito_q, comentario_q):
                    st.success("Questão adicionada!")

with st.expander("🛠️ ETAPA 4: Editar Questão Existente", expanded=True):
    if not opcoes_pastas:
        st.info("Cadastre pastas e questões primeiro.")
    else:
        st.markdown("Isolamos as modalidades para manter a organização. Escolha a pasta e o tipo de treino.")
        colEd1, colEd2 = st.columns(2)
        with colEd1:
            pasta_edicao = st.selectbox("1. Pasta Alvo:", list(opcoes_pastas.keys()), key="sel_pasta_ed")
        with colEd2:
            mod_edicao = st.selectbox("2. Tipo de Questão:", ["Lei Seca - Cebraspe (CE)", "Gerais - Múltipla Escolha (ME)"], key="sel_mod_ed")
            sigla_mod_ed = "CE" if "CE" in mod_edicao else "ME"
        
        id_pasta_ed = opcoes_pastas[pasta_edicao]
        questoes_disponiveis = buscar_questoes_por_filtro(id_pasta_ed, sigla_mod_ed)
        
        if not questoes_disponiveis:
            st.warning("Nenhuma questão dessa modalidade encontrada nesta pasta.")
        else:
            questao_sel_str = st.selectbox("3. Selecione a Questão para Edição:", list(questoes_disponiveis.keys()), key="sel_q_ed")
            q_alvo = questoes_disponiveis[questao_sel_str]
            
            colM1, colM2, colM3 = st.columns([1,1,2])
            with colM1: nova_banca = st.text_input("Banca", value=q_alvo.banca, key="ed_banca")
            with colM2: novo_ano = st.number_input("Ano", value=q_alvo.ano, key="ed_ano")
            with colM3:
                if sigla_mod_ed == "CE":
                    novo_gab = st.selectbox("Novo Gabarito", ["C", "E"], index=["C", "E"].index(q_alvo.gabarito), key="ed_gab_ce")
                else:
                    opcoes_me = ["A", "B", "C", "D", "E"]
                    idx_gab = opcoes_me.index(q_alvo.gabarito) if q_alvo.gabarito in opcoes_me else 0
                    novo_gab = st.selectbox("Novo Gabarito", opcoes_me, index=idx_gab, key="ed_gab_me")
            
            st.markdown("**Enunciado da Questão (Edite Aqui)**")
            novo_enunciado = st_quill(value=q_alvo.enunciado, key=f"ed_enunc_{q_alvo.id}")
            
            novas_alternativas = None
            if sigla_mod_ed == "ME":
                st.markdown("**Alternativas (Edite Aqui)**")
                alt_atuais = q_alvo.alternativas or {"A": "", "B": "", "C": "", "D": "", "E": ""}
                
                colAlt1, colAlt2 = st.columns(2)
                with colAlt1:
                    alt_a = st.text_input("A)", value=alt_atuais.get("A", ""), key=f"ed_A_{q_alvo.id}")
                    alt_b = st.text_input("B)", value=alt_atuais.get("B", ""), key=f"ed_B_{q_alvo.id}")
                    alt_c = st.text_input("C)", value=alt_atuais.get("C", ""), key=f"ed_C_{q_alvo.id}")
                with colAlt2:
                    alt_d = st.text_input("D)", value=alt_atuais.get("D", ""), key=f"ed_D_{q_alvo.id}")
                    alt_e = st.text_input("E)", value=alt_atuais.get("E", ""), key=f"ed_E_{q_alvo.id}")
                
                novas_alternativas = {"A": alt_a, "B": alt_b, "C": alt_c, "D": alt_d, "E": alt_e}

            st.markdown("**Comentário Estratégico (Edite Aqui)**")
            novo_coment = st_quill(value=q_alvo.comentario_teorico, key=f"ed_coment_{q_alvo.id}")
            
            if st.button("💾 Salvar Alterações na Questão", type="primary"):
                if atualizar_questao(q_alvo.id, nova_banca, novo_ano, novo_gab, novo_enunciado, novas_alternativas, novo_coment):
                    st.success("✅ Questão atualizada com sucesso! O carro está pronto para a pista.")
                    st.rerun()
