import json

from pathlib import Path
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "tema": "escuro",
    "ors_api_key": "",
    "tentativas_extras": 2,
    "tempo_espera": 2,
    "percentual_adicional": 0.0015
}


def carregar_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}

    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)

    return cfg


def salvar_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
