import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Busca a URL (Simples e direto)
URL = os.environ.get("DATABASE_URL")

# 2. Motor padrão (O Streamlit cuida do resto)
engine = create_engine(URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Suas Tabelas Essenciais
class Questao(Base):
    __tablename__ = 'tb_questao'
    id = Column(Integer, primary_key=True)
    enunciado = Column(Text, nullable=False)
    gabarito = Column(String, nullable=False)
    modalidade = Column(String) # CE ou ME

class Historico(Base):
    __tablename__ = 'tb_historico'
    id = Column(Integer, primary_key=True)
    acertou = Column(Boolean)

# Criar tabelas
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Banco pronto!")
