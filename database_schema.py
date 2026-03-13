import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
import datetime

# Tenta pegar do Secrets (Nuvem) ou do ambiente local
url_banco = os.environ.get("DATABASE_URL")

if not url_banco:
    raise ValueError("🚨 DATABASE_URL não encontrada nos Secrets do Streamlit!")

if url_banco.startswith("postgres://"):
    url_banco = url_banco.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    url_banco,
    pool_size=5,           # Mantém 5 conexões prontas
    max_overflow=10,       # Abre mais se precisar
    pool_timeout=30,       # Espera 30s antes de dar erro
    pool_recycle=1800,     # Reinicia conexões a cada 30min
    pool_pre_ping=True     # Testa se a conexão caiu antes de cada clique
)
Base = declarative_base()

# --- Definição das Tabelas ---
class Disciplina(Base):
    __tablename__ = 'tb_disciplina'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    subtemas = relationship("Subtema", back_populates="disciplina")

class Subtema(Base):
    __tablename__ = 'tb_subtema'
    id = Column(Integer, primary_key=True)
    id_disciplina = Column(Integer, ForeignKey('tb_disciplina.id'))
    nome = Column(String, nullable=False)
    disciplina = relationship("Disciplina", back_populates="subtemas")
    assuntos = relationship("Assunto", back_populates="subtema")

class Assunto(Base):
    __tablename__ = 'tb_assunto'
    id = Column(Integer, primary_key=True)
    id_subtema = Column(Integer, ForeignKey('tb_subtema.id'))
    nome = Column(String, nullable=False)
    subtema = relationship("Subtema", back_populates="assuntos")
    questoes = relationship("Questao", back_populates="assunto")
    conteudos = relationship("ConteudoTeorico", back_populates="assunto")

class ConteudoTeorico(Base):
    __tablename__ = 'tb_conteudo_teorico'
    id = Column(Integer, primary_key=True)
    id_assunto = Column(Integer, ForeignKey('tb_assunto.id'))
    titulo = Column(String, nullable=False)
    url_video = Column(String, nullable=True) 
    texto_rico = Column(Text, nullable=False)
    assunto = relationship("Assunto", back_populates="conteudos")
    questoes_vinculadas = relationship("Questao", back_populates="conteudo_teorico")

class Questao(Base):
    __tablename__ = 'tb_questao'
    id = Column(Integer, primary_key=True)
    banca = Column(String)
    ano = Column(Integer)
    id_assunto = Column(Integer, ForeignKey('tb_assunto.id'))
    id_conteudo = Column(Integer, ForeignKey('tb_conteudo_teorico.id'), nullable=True)
    modalidade = Column(String)
    enunciado = Column(Text, nullable=False)
    alternativas = Column(JSON, nullable=True) 
    gabarito = Column(String, nullable=False)
    comentario_teorico = Column(Text)
    assunto = relationship("Assunto", back_populates="questoes")
    conteudo_teorico = relationship("ConteudoTeorico", back_populates="questoes_vinculadas")

class HistoricoResolucao(Base):
    __tablename__ = 'tb_historico'
    id = Column(Integer, primary_key=True)
    id_questao = Column(Integer, ForeignKey('tb_questao.id'))
    resposta_marcada = Column(String, nullable=False)
    acertou = Column(Boolean, nullable=False)
    data_resolucao = Column(DateTime, default=datetime.datetime.utcnow)
    questao = relationship("Questao")

class Edital(Base):
    __tablename__ = 'tb_edital'
    id = Column(Integer, primary_key=True)
    nome_concurso = Column(String, nullable=False) 
    cargo = Column(String, nullable=False) 
    banca = Column(String, nullable=True)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Tabelas sincronizadas!")
