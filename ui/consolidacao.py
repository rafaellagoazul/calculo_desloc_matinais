
from pathlib import Path
import pandas as pd
COLUNAS_CORE = [
    "SV",
    "DIA",
    "COD VENDEDOR",
    "COD CLIENTE",
    "CASA VEND",
    "DISTRIBUIDOR",
    "1ºCLIENTE",
    "CASA→DIST→CLI",
    "CASA→CLI",
    "DIFERENÇA",
]


def consolidar_arquivos(arquivos):
    frames = []

    for caminho in arquivos:
        caminho = Path(caminho)

        if not caminho.exists():
            continue

        try:
            xls = pd.ExcelFile(caminho)
        except Exception:
            continue

        for aba in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=aba)
            except Exception:
                continue

            if df.empty:
                continue

            # normaliza colunas
            colunas = [str(c).strip() for c in df.columns]

            if colunas != COLUNAS_CORE:
                continue  # não é saída oficial do core

            df.columns = COLUNAS_CORE

            # remove linhas vazias
            df = df.dropna(how="all")

            # metadados úteis
            df["ARQUIVO_ORIGEM"] = caminho.name
            df["ABA_ORIGEM"] = aba

            frames.append(df)

    if not frames:
        raise RuntimeError(
            "Nenhum dado válido encontrado para consolidação.\n"
            "Verifique se os arquivos são saídas do processamento."
        )

    consolidado = pd.concat(frames, ignore_index=True)

    # ordenação lógica
    consolidado = consolidado.sort_values(
        ["DIA", "SV", "COD VENDEDOR", "COD CLIENTE"],
        ignore_index=True
    )

    return consolidado
