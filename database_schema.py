import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

# ==========================================
# 🔌 MOTOR DE CONEXÃO SUPABASE (SERVERLESS MODE)
# ==========================================

url_raw = os.environ.get("DATABASE_URL")

if not url_raw:
    raise ValueError("🚨 DATABASE_URL não encontrada nos Secrets!")

# Correção automática de protocolo para SQLAlchemy 2.0+
if url_raw.startswith("postgres://"):
    url_raw = url_raw.replace("postgres://", "postgresql://", 1)

# Criamos o motor com as flags de estabilidade para PGBouncer
engine = create_engine(
    url_raw,
    pool_pre_ping=True,      # Testa a saúde da conexão antes de usar
    pool_size=1,             # Em serverless, menos é mais (evita travar o pool)
    max_overflow=0,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10
    }
)

Base = declarative_base()

# ==========================================
# 🏛️ MODELOS (MANTIDOS)
# ==========================================
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

class Questao(Base):
    __tablename__ = 'tb_questao'
    id = Column(Integer, primary_key=True)
    banca = Column(String)
    ano = Column(Integer)
    id_assunto = Column(Integer, ForeignKey('tb_assunto.id'))
    modalidade = Column(String) 
    enunciado = Column(Text, nullable=False)
    alternativas = Column(JSON, nullable=True) 
    gabarito = Column(String, nullable=False)
    comentario_teorico = Column(Text)
    assunto = relationship("Assunto", back_populates="questoes")

class HistoricoResolucao(Base):
    __tablename__ = 'tb_historico'
    id = Column(Integer, primary_key=True)
    id_questao = Column(Integer, ForeignKey('tb_questao.id'))
    resposta_marcada = Column(String, nullable=False)
    acertou = Column(Boolean, nullable=False)
    data_resolucao = Column(DateTime, default=datetime.datetime.utcnow)

# ==========================================
# 🛠️ SINCRONIZAÇÃO INICIAL
# ==========================================
if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("✅ GestoBap: Tabelas sincronizadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro crítico de conexão: {e}")
