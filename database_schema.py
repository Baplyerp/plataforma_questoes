import os
import datetime
import ssl
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

# ==========================================
# 🔌 CONFIGURAÇÃO DE CONEXÃO (ARQUITETURA NUVEM)
# ==========================================

# Pegamos os segredos organizados do Streamlit
db_secrets = os.environ.get("database") # Para local ou se estiver flat
if not db_secrets:
    # Se o Streamlit não converter o TOML em env vars automaticamente, pegamos manualmente
    import streamlit as st
    db_config = st.secrets["database"]
else:
    # Caso o Streamlit injete como env vars
    import streamlit as st
    db_config = st.secrets["database"]

# Montamos a URL garantindo o driver correto
db_url = f"postgresql+pg8000://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Contexto SSL para o pg8000 (Obrigatório para Supabase)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_engine(
    db_url,
    connect_args={
        "ssl_context": ssl_ctx,
        "timeout": 60
    },
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20
)

Base = declarative_base()

# ==========================================
# 🏛️ MODELOS DAS TABELAS (MANTIDOS)
# ==========================================
# ... (Mantenha todas as classes: Disciplina, Subtema, Assunto, Questao, etc., como já criamos)

# ==========================================
# 🛠️ SINCRONIZAÇÃO
# ==========================================

if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("✅ Tabelas sincronizadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro de Sincronização: {e}")
