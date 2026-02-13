from pathlib import Path
import sqlite3

# Caminho do banco
DB_PATH = Path("data/deslocamentos.db")


def inicializar_db():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deslocamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sv TEXT NOT NULL,
            dia TEXT NOT NULL,
            cod_vendedor TEXT NOT NULL,
            cod_cliente TEXT NOT NULL,

            casa_vend TEXT,
            distribuidor TEXT,
            primeiro_cliente TEXT,

            dist_casa_cli REAL,
            dist_casa_dist_cli REAL,
            diferenca REAL,

            origem_arquivo TEXT NOT NULL,

            hash_registro TEXT NOT NULL UNIQUE,
            criado_em TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def inserir_registros(registros: list[dict], origem_arquivo: str):
    """
    Insere os registros calculados no banco de dados.
    """
    if not registros:
        return 0, 0

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inseridos = 0
    duplicados = 0

    campos_obrigatorios = [
        "sv",
        "dia",
        "cod_vendedor",
        "cod_cliente",
        "casa_vend",
        "distribuidor",
        "primeiro_cliente",
        "dist_casa_cli",
        "dist_casa_dist_cli",
        "diferenca",
        "hash_registro",
    ]

    for r in registros:
        for campo in campos_obrigatorios:
            if campo not in r:
                raise KeyError(f"Campo ausente no registro: {campo}")

        try:
            cur.execute("""
                INSERT INTO deslocamentos (
                    sv,
                    dia,
                    cod_vendedor,
                    cod_cliente,
                    casa_vend,
                    distribuidor,
                    primeiro_cliente,
                    dist_casa_cli,
                    dist_casa_dist_cli,
                    diferenca,
                    origem_arquivo,
                    hash_registro,
                    criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                r["sv"],
                r["dia"],
                r["cod_vendedor"],
                r["cod_cliente"],
                r["casa_vend"],
                r["distribuidor"],
                r["primeiro_cliente"],
                r["dist_casa_cli"],
                r["dist_casa_dist_cli"],
                r["diferenca"],
                origem_arquivo,
                r["hash_registro"],
            ))

            inseridos += 1

        except sqlite3.IntegrityError:
            duplicados += 1

    conn.commit()
    conn.close()

    return inseridos, duplicados
