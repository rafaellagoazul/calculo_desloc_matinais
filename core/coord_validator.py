from typing import Tuple
"""
Validação e parsing de coordenadas geográficas.

Objetivos:
- Parsing tolerante (compatível com a v1.0)
- Diferenciar ERRO real de ALERTA
- Não bloquear fluxo cedo demais
- Fornecer motivo claro para UI / mapa
"""
from typing import Optional, Tuple



def _to_float(valor) -> Optional[float]:
    """
    Converte valores variados para float de forma tolerante.
    Aceita vírgula decimal, espaços e strings.
    """
    if valor is None:
        return None
    try:
        s = str(valor).strip().replace(",", ".")
        if s == "":
            return None
        return float(s)
    except Exception:
        return None


def validar_coordenada(lat, lon, label: str = "Coordenada") -> Tuple[bool, Optional[str]]:
    """
    Valida uma coordenada geográfica.

    RETORNO (compatível com o sistema atual):
        (ok: bool, motivo: str | None)

    Convenção do motivo:
        - None            → OK
        - "ALERTA: ..."   → Coordenada suspeita, mas utilizável
        - "ERRO: ..."     → Coordenada inválida (bloqueante)
    """

    # ───────── Nulos / vazios ─────────
    if lat in (None, "", " ") or lon in (None, "", " "):
        return False, f"ERRO: {label}: latitude ou longitude vazia ({lat}, {lon})"

    # ───────── Parsing tolerante ─────────
    lat_f = _to_float(lat)
    lon_f = _to_float(lon)

    if lat_f is None or lon_f is None:
        return False, f"ERRO: {label}: valor não numérico ({lat}, {lon})"

    # ───────── Limites globais (erro real) ─────────
    if not (-90 <= lat_f <= 90):
        return False, f"ERRO: {label}: latitude fora do intervalo (-90 a 90): {lat_f}"

    if not (-180 <= lon_f <= 180):
        return False, f"ERRO: {label}: longitude fora do intervalo (-180 a 180): {lon_f}"

    # ───────── Coordenada zero (suspeita, mas não erro fatal) ─────────
    if lat_f == 0 or lon_f == 0:
        return True, f"ALERTA: {label}: coordenada zero (possível erro de geocoding)"

    # ───────── OK ─────────
    return True, None
