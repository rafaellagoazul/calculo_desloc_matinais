import sqlite3
from datetime import datetime
from ui.db import DB_PATH



def inicializar_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT,
            registros INTEGER,
            tempo REAL,
            status TEXT,
            data TEXT
        )
    """)

    conn.commit()
    conn.close()


def registrar_execucao(
    arquivo,
    registros=0,
    tempo=0.0,
    status="OK"
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO historico (
            arquivo, registros, tempo, status, data
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        str(arquivo),
        registros,
        round(tempo, 2),
        status,
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def listar_execucoes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT arquivo, registros, tempo, status, data
        FROM historico
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return rows

def limpar_execucoes():
    import sqlite3
    conn = sqlite3.connect("data/historico.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM historico_execucoes")
    conn.commit()
    conn.close()

def garantir_coluna(cur, nome, tipo):
    cur.execute("PRAGMA table_info(deslocamentos)")
    colunas = [c[1] for c in cur.fetchall()]
    if nome not in colunas:
        cur.execute(f"ALTER TABLE deslocamentos ADD COLUMN {nome} {tipo}")
        garantir_coluna(cur, "origem_arquivo", "TEXT")
        garantir_coluna(cur, "criado_em", "TEXT")
        garantir_coluna(cur, "hash_registro", "TEXT")

def listar_execucoes_por_arquivo(nome_arquivo: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT arquivo, registros, tempo, status, data
        FROM execucoes
        WHERE arquivo LIKE ?
        ORDER BY data DESC
    """, (f"%{nome_arquivo}%",))

    rows = cur.fetchall()
    conn.close()
    return rows

def _fetch_all(sql: str, params: list | tuple = ()):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows


# ============================================================
# PESQUISA AVANÇADA DE HISTÓRICO
# ============================================================

def buscar_historico_avancado(
    texto=None,
    status=None,
    data_ini=None,
    data_fim=None,
    limite=200
):
    # fallback automático — compatibilidade com UI antiga
    if not any([texto, status, data_ini, data_fim]):
        try:
            return listar_execucoes()
        except Exception:
            pass
    """
    Pesquisa combinável e case-insensitive no histórico.
    Todos os parâmetros são opcionais.
    """

    filtros = []
    params = []

    if texto:
        filtros.append("(LOWER(arquivo) LIKE ?)")
        params.append(f"%{texto.lower()}%")

    if status:
        filtros.append("status = ?")
        params.append(status)

    if data_ini:
        filtros.append("data >= ?")
        params.append(data_ini)

    if data_fim:
        filtros.append("data <= ?")
        params.append(data_fim)

    where = ""
    if filtros:
        where = "WHERE " + " AND ".join(filtros)

    sql = f"""
        SELECT
            id,
            arquivo,
            registros,
            tempo,
            status,
            data
        FROM historico
        {where}
        ORDER BY data DESC
        LIMIT ?
    """

    params.append(limite)

    return _fetch_all(sql, params)

    