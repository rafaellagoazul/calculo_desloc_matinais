# core/preprocessador_coordenadas.py

from pathlib import Path
import pandas as pd


class PreProcessadorCoordenadas:
    """
    Pré-processador neutro.

    - NÃO valida
    - NÃO corrige
    - NÃO interage
    - Apenas carrega o Excel e entrega ao core
    """

    def __init__(self, arquivo_excel: Path, on_log=None):
        self.arquivo_excel = Path(arquivo_excel)
        self.on_log = on_log or (lambda msg: None)

    # ======================================================
    def processar(self) -> pd.DataFrame:
        self.on_log("📥 Carregando planilha (sem validação de coordenadas)")
        return pd.read_excel(self.arquivo_excel)
