import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship
import datetime

# 1. Ele lê o arquivo .env escondido no seu PC
load_dotenv()

# 2. Ele puxa a URL segura lá de dentro
url_banco = os.getenv("DATABASE_URL")

# 3. Ele conecta o motor da Baply no Supabase
engine = create_engine(url_banco)
Base = declarative_base()

# ==========================================
# 1. TAXONOMIA (A Árvore do Conhecimento)
# ==========================================
class Disciplina(Base):
    __tablename__ = 'tb_disciplina'
    __table_args__ = {'extend_existing': True} # Blinda contra o erro do Streamlit
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    subtemas = relationship("Subtema", back_populates="disciplina")

class Subtema(Base):
    __tablename__ = 'tb_subtema'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_disciplina = Column(Integer, ForeignKey('tb_disciplina.id'))
    nome = Column(String, nullable=False)
    
    disciplina = relationship("Disciplina", back_populates="subtemas")
    assuntos = relationship("Assunto", back_populates="subtema")

class Assunto(Base):
    __tablename__ = 'tb_assunto'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_subtema = Column(Integer, ForeignKey('tb_subtema.id'))
    nome = Column(String, nullable=False)
    
    subtema = relationship("Subtema", back_populates="assuntos")
    questoes = relationship("Questao", back_populates="assunto")
    conteudos = relationship("ConteudoTeorico", back_populates="assunto")

# ==========================================
# 2. CONTEÚDO TEÓRICO (Sua Base de Conhecimento)
# ==========================================
class ConteudoTeorico(Base):
    __tablename__ = 'tb_conteudo_teorico'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_assunto = Column(Integer, ForeignKey('tb_assunto.id'))
    titulo = Column(String, nullable=False)
    url_video = Column(String, nullable=True) # <-- Nosso campo para o YouTube!
    texto_rico = Column(Text, nullable=False)
    
    assunto = relationship("Assunto", back_populates="conteudos")
    questoes_vinculadas = relationship("Questao", back_populates="conteudo_teorico")

# ==========================================
# 3. TABELA DE QUESTÕES (Agora Turbinada)
# ==========================================
class Questao(Base):
    __tablename__ = 'tb_questao'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    banca = Column(String)
    ano = Column(Integer)
    id_assunto = Column(Integer, ForeignKey('tb_assunto.id'))
    nivel = Column(String) 
    dificuldade = Column(String) 
    id_conteudo = Column(Integer, ForeignKey('tb_conteudo_teorico.id'), nullable=True)
    modalidade = Column(String)
    enunciado = Column(Text, nullable=False)
    alternativas = Column(JSON, nullable=True) 
    gabarito = Column(String, nullable=False)
    comentario_teorico = Column(Text)
    
    assunto = relationship("Assunto", back_populates="questoes")
    conteudo_teorico = relationship("ConteudoTeorico", back_populates="questoes_vinculadas")

# ==========================================
# 4. TABELA DE DESEMPENHO (Seu Histórico)
# ==========================================
class HistoricoResolucao(Base):
    __tablename__ = 'tb_historico'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_questao = Column(Integer, ForeignKey('tb_questao.id'))
    resposta_marcada = Column(String, nullable=False)
    acertou = Column(Boolean, nullable=False)
    data_resolucao = Column(DateTime, default=datetime.datetime.utcnow)
    questao = relationship("Questao")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Novo Banco de Dados Multi-Relacional criado com sucesso!")

# ==========================================
# 5. GESTÃO DE ESTUDOS E NEUROCIÊNCIA (O Motor da Baply)
# ==========================================

class Edital(Base):
    """O alvo atual. Ex: Analista de Controle Interno de Catende"""
    __tablename__ = 'tb_edital'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    nome_concurso = Column(String, nullable=False) 
    cargo = Column(String, nullable=False) 
    banca = Column(String, nullable=True)
    data_prova = Column(DateTime, nullable=True)
    ativo = Column(Boolean, default=True) # Para focar em um edital de cada vez
    
    materias = relationship("MateriaCiclo", back_populates="edital", cascade="all, delete-orphan")

class MateriaCiclo(Base):
    """A engrenagem do Ciclo de Estudos intercalado"""
    __tablename__ = 'tb_materia_ciclo'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_edital = Column(Integer, ForeignKey('tb_edital.id'))
    nome = Column(String, nullable=False) # Ex: AFO, Direito Administrativo
    peso = Column(Integer, default=1)
    carga_horaria_meta_minutos = Column(Integer, nullable=False) # O tempo alocado no ciclo (Ex: 90 min)
    cor_hex = Column(String, default="#3B82F6") # Para os gráficos do frontend
    
    edital = relationship("Edital", back_populates="materias")
    sessoes = relationship("SessaoEstudo", back_populates="materia")

class SessaoEstudo(Base):
    """O log de telemetria de cada sentada na cadeira"""
    __tablename__ = 'tb_sessao_estudo'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    id_materia = Column(Integer, ForeignKey('tb_materia_ciclo.id'))
    data_sessao = Column(DateTime, default=datetime.datetime.utcnow)
    duracao_minutos = Column(Integer, nullable=False)
    metodo_utilizado = Column(String) # Ex: Ultradiano (90m), Pomodoro (25m), Ciclo Livre
    foco_rating = Column(Integer) # Nota de 1 a 5 do próprio usuário sobre o foco (Neurociência)
    
    materia = relationship("MateriaCiclo", back_populates="sessoes")

class HistoricoConcurso(Base):
    """O mapeamento da evolução real contra a concorrência (Sua ideia futura)"""
    __tablename__ = 'tb_historico_concurso'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    orgao = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    nota_final = Column(Float)
    posicao = Column(Integer)
    nota_corte = Column(Float)
    concorrencia_total = Column(Integer, nullable=True)

    if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Novo Banco de Dados Multi-Relacional criado com sucesso!")


    
