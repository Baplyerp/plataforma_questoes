import os
import datetime
import ssl
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

# ==========================================
# 🔌 CONFIGURAÇÃO DE CONEXÃO (NUVEM)
# ==========================================

url_banco = os.environ.get("DATABASE_URL")

if not url_banco:
    raise ValueError("🚨 DATABASE_URL não encontrada nos Secrets do Streamlit!")

# Forçamos o driver pg8000 (mais estável para Python 3.14 na nuvem)
if url_banco.startswith("postgresql://"):
    url_banco = url_banco.replace("postgresql://", "postgresql+pg8000://", 1)

# Criamos um contexto SSL compatível para o pg8000 atravessar o firewall do Streamlit
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_engine(
    url_banco,
    connect_args={"ssl_context": ssl_ctx},
    pool_pre_ping=True,                # Testa a conexão antes de cada uso
    pool_recycle=300,                  # Limpa conexões inativas a cada 5 min
    pool_size=5,                       # Mantém um pool fixo de conexões
    max_overflow=10                    # Permite expansão se houver muitos cliques
)

Base = declarative_base()

# ==========================================
# 🏛️ DEFINIÇÃO DAS TABELAS (MODELOS)
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

# ==========================================
# 🛠️ EXECUÇÃO (SINCRONIZAÇÃO)
# ==========================================

if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("✅ GestoBap: Tabelas sincronizadas com sucesso no Supabase!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar tabelas: {e}")
