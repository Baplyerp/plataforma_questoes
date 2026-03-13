import os
import datetime
import ssl
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

# ==========================================
# 🔌 CONFIGURAÇÃO DE CONEXÃO (BLINDADA)
# ==========================================

url_banco = os.environ.get("DATABASE_URL")

if not url_banco:
    raise ValueError("🚨 DATABASE_URL não encontrada nos Secrets do Streamlit!")

# 1. Ajuste de Protocolo para pg8000
if url_banco.startswith("postgresql://") or url_banco.startswith("postgres://"):
    url_banco = url_banco.replace("postgresql://", "postgresql+pg8000://", 1)
    url_banco = url_banco.replace("postgres://", "postgresql+pg8000://", 1)

# 2. LIMPEZA CRÍTICA: Remove o '?pgbouncer=true' ou qualquer lixo da URL
# O pg8000 não aceita argumentos de query string na URL via SQLAlchemy
if "?" in url_banco:
    url_banco = url_banco.split("?")[0]

# 3. Configuração de SSL (Obrigatória para Supabase)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# 4. Criação do Motor
engine = create_engine(
    url_banco,
    connect_args={
        "ssl_context": ssl_ctx,
        "timeout": 30
    },
    pool_pre_ping=True,  # Testa a conexão antes de usar (evita quedas)
    pool_recycle=1800    # Reinicia conexões a cada 30 min
)

Base = declarative_base()

# ==========================================
# 🏛️ MODELOS DAS TABELAS
# ==========================================

class Disciplina(Base):
    __tablename__ = 'tb_disciplina'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    subtemas = relationship("Subtema", back_populates="disciplina", cascade="all, delete-orphan")

class Subtema(Base):
    __tablename__ = 'tb_subtema'
    id = Column(Integer, primary_key=True)
    id_disciplina = Column(Integer, ForeignKey('tb_disciplina.id'))
    nome = Column(String, nullable=False)
    disciplina = relationship("Disciplina", back_populates="subtemas")
    assuntos = relationship("Assunto", back_populates="subtema", cascade="all, delete-orphan")

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
    modalidade = Column(String) # 'CE' ou 'ME'
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

# --- Sincronização ---
if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("✅ GestoBap: Tabelas sincronizadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")
