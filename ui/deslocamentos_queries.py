# ==========================================================
# 🔒 QUERIES DE DESLOCAMENTOS — FONTE ÚNICA DA UI
# ==========================================================

import sqlite3
from pathlib import Path

# ----------------------------------------------------------
# DB
# ----------------------------------------------------------

def get_db_path() -> Path:
    return Path("data/deslocamentos.db")


# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------

def _fetch_all(sql: str, params: list | tuple = ()):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------
# LISTAGEM BÁSICA (SEM FILTROS)
# ----------------------------------------------------------

def listar_deslocamentos(
    periodo: str | None = None,
    vendedor: str | None = None,
    limite: int = 500
):
    filtros = []
    params = []

    if periodo:
        filtros.append("dia = ?")
        params.append(periodo)

    if vendedor:
        filtros.append("cod_vendedor = ?")
        params.append(vendedor)

    where = ""
    if filtros:
        where = "WHERE " + " AND ".join(filtros)

    sql = f"""
        SELECT
            id,
            cod_vendedor,
            dia,
            dist_casa_cli,
            dist_casa_dist_cli,
            diferenca,
            origem_arquivo,
            substr(dia, 1, 7) AS periodo
        FROM deslocamentos
        {where}
        ORDER BY id DESC
        LIMIT ?
    """

    params.append(limite)
    return _fetch_all(sql, params)


# ----------------------------------------------------------
# 🔎 PESQUISA AVANÇADA (HISTORY WINDOW)
# ----------------------------------------------------------

def buscar_deslocamentos_avancado(
    texto=None,
    vendedor=None,
    data_ini=None,
    data_fim=None
):
    print("🧪 DEBUG QUERY")
    print("texto:", texto)
    print("vendedor:", vendedor)
    print("data_ini:", data_ini)
    print("data_fim:", data_fim)

    sql = """
        SELECT
            id,
            cod_vendedor,
            dia,
            dist_casa_cli,
            dist_casa_dist_cli,
            diferenca,
            origem_arquivo,
            criado_em
        FROM deslocamentos
        WHERE 1=1
    """
    params = []

    if texto:
        sql += " AND origem_arquivo LIKE ?"
        params.append(f"%{texto}%")

    if vendedor:
        sql += " AND cod_vendedor LIKE ?"
        params.append(f"%{vendedor}%")

    if data_ini and data_fim:
        sql += " AND date(criado_em) BETWEEN ? AND ?"
        params.extend([data_ini, data_fim])

    sql += " ORDER BY criado_em DESC"

    print("SQL:", sql)
    print("PARAMS:", params)

    return _fetch_all(sql, params)
