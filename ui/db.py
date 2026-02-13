import sqlite3
from pathlib import Path


DB_PATH = Path("data/deslocamentos.db")
DB_PATH.parent.mkdir(exist_ok=True)


def get_conn():
    """
    Retorna conexão SQLite padronizada para todo o projeto.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deslocamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_vendedor TEXT NOT NULL,
            dia TEXT NOT NULL,
            dist_casa_cli REAL,
            dist_casa_dist_cli REAL,
            diferenca REAL,
            criado_em TEXT,
            origem_arquivo TEXT,
            hash_registro TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()