import json
import time
import threading
import hashlib

import requests

from core.coord_validator import validar_coordenada


from pathlib import Path
import pandas as pd
class CalculadorDeslocamentos:
    """
    CORE DE CÁLCULO
    ----------------
    • NÃO corrige coordenadas
    • NÃO chama mapa
    • NÃO tenta adivinhar localização
    • Assume dados já validados
    """

    def __init__(
        self,
        arquivo_excel: Path,
        ors_api_key: str,
        on_log=None,
        on_progress=None,
        cancel_event: threading.Event | None = None,
        tentativas_extras: int = 2,
        tempo_espera: int = 2,
        percentual_adicional: float = 0.0,
        salvar_excel: bool = False,
        emitter=None,  # ⬅️ NOVO (opcional, não quebra)
    ):
        self.arquivo_excel = Path(arquivo_excel)
        self.ors_api_key = ors_api_key

        self.on_log = on_log or (lambda msg: None)
        self.on_progress = on_progress or (lambda atual, total: None)
        self.on_fail = None

        self.emitter = emitter  # ⬅️ NOVO

        self.cancel_event = cancel_event or threading.Event()

        self.tentativas_extras = tentativas_extras
        self.tempo_espera = tempo_espera
        self.percentual_adicional = percentual_adicional
        self.salvar_excel = salvar_excel

        self.cache_dir = Path(".cache_ors")
        self.cache_dir.mkdir(exist_ok=True)

    # ======================================================
    # PROCESSAMENTO PRINCIPAL
    # ======================================================
    def calcular(self) -> list[dict]:
        inicio = time.time()
        self._log("=== Início do cálculo de deslocamentos ===")

        df = pd.read_excel(self.arquivo_excel)
        df = self._validar_colunas(df)

        total_linhas = len(df)
        passos_por_linha = 4
        total_passos = total_linhas * passos_por_linha
        passo_atual = 0

        def _avancar_progresso():
            nonlocal passo_atual
            passo_atual += 1
            self._progresso(passo_atual, total_passos)

        resultados: list[dict] = []

        for idx, row in df.iterrows():
            if self.cancel_event.is_set():
                self._log("⛔ Processamento cancelado")
                break

            linha_excel = idx + 2
            self._log(f"🔄 Linha {linha_excel}/{total_linhas + 1}")

            casa = self._parse_coord(row["CASA VEND"])
            dist = self._parse_coord(row["DISTRIBUIDOR"])
            cli = self._parse_coord(row["1ºCLIENTE"])

            self._validar_ou_falhar(casa, "CASA VEND", linha_excel)
            self._validar_ou_falhar(dist, "DISTRIBUIDOR", linha_excel)
            _avancar_progresso()

            try:
                d1 = self._rota_com_tentativas(
                    casa, dist, linha_excel, "CASA VEND", "DISTRIBUIDOR"
                )
                _avancar_progresso()

                d2 = 0
                if cli:
                    self._validar_ou_falhar(cli, "1ºCLIENTE", linha_excel)
                    d2 = self._rota_com_tentativas(
                        dist, cli, linha_excel, "DISTRIBUIDOR", "1ºCLIENTE"
                    )
                _avancar_progresso()

                d3 = 0
                if cli:
                    d3 = self._rota_com_tentativas(
                        casa, cli, linha_excel, "CASA VEND", "1ºCLIENTE"
                    )
                _avancar_progresso()

                fator = 1 + self.percentual_adicional

                registro = {
                    "sv": row.get("SV"),
                    "dia": row.get("DIA"),
                    "cod_vendedor": row.get("COD VENDEDOR"),
                    "cod_cliente": row.get("COD CLIENTE"),
                    "casa_vend": row["CASA VEND"],
                    "distribuidor": row["DISTRIBUIDOR"],
                    "primeiro_cliente": row["1ºCLIENTE"],
                    "dist_casa_dist_cli": round((d1 + d2) * fator / 1000, 2),
                    "dist_casa_cli": round(d3 * fator / 1000, 2),
                    "diferenca": round(((d1 + d2) - d3) * fator / 1000, 2),
                }

                registro["hash_registro"] = self._gerar_hash_registro(registro)
                resultados.append(registro)

                self._log(f"✅ Linha {linha_excel} — OK")

            except Exception as e:
                self._log(f"❌ Linha {linha_excel} — ERRO: {e}")
                continue

        if self.salvar_excel and resultados:
            self._salvar_excel_resultados(resultados)

        self._log(f"⏱ Tempo total: {int(time.time() - inicio)}s")
        self._log("=== Fim do cálculo ===")

        self._emit("concluido", resultados)
        return resultados

    # ======================================================
    # EVENTOS / LOG / PROGRESSO
    # ======================================================
    def _emit(self, tipo, payload):
        if self.emitter:
            try:
                self.emitter.emit(tipo, payload)
            except Exception:
                pass  # nunca deixa o core quebrar por evento

    def _log(self, msg):
        self.on_log(msg)
        self._emit("log", msg)

    def _progresso(self, atual, total):
        self.on_progress(atual, total)
        self._emit("progresso", {"atual": atual, "total": total})

    # ======================================================
    # SALVAR RESULTADOS
    # ======================================================
    def _salvar_excel_resultados(self, resultados: list[dict]):
        nome_saida = self.arquivo_excel.with_name(
            f"{self.arquivo_excel.stem}_resultados.xlsx"
        )

        df = pd.DataFrame(resultados)
        df.to_excel(nome_saida, index=False)

        self._log(f"💾 Resultados salvos em: {nome_saida.resolve()}")

    # ======================================================
    # AUXILIARES
    # ======================================================
    def _validar_ou_falhar(self, coord, label, linha):
        if not coord:
            self._falha(linha, label, "—", f"{label}: coordenada ausente")
            raise RuntimeError("Coordenada inválida")

        ok, erro = validar_coordenada(coord[0], coord[1], label)
        if not ok:
            self._falha(linha, label, "—", erro)
            raise RuntimeError("Coordenada inválida")

    def _rota_com_tentativas(self, origem, destino, linha, nome_origem, nome_destino):
        total = self.tentativas_extras + 1

        for tentativa in range(1, total + 1):
            if self.cancel_event.is_set():
                raise RuntimeError("Processamento cancelado")

            try:
                return self._rota(origem, destino)
            except Exception:
                if tentativa >= total:
                    self._falha(
                        linha,
                        nome_origem,
                        nome_destino,
                        f"Falhou após {tentativa} tentativas (ORS)"
                    )
                    raise

                self._log(
                    f"⚠ Linha {linha} — tentativa {tentativa}/{total} "
                    f"({nome_origem} → {nome_destino})"
                )
                time.sleep(self.tempo_espera)

    def _rota(self, origem, destino):
        chave = self._cache_key(origem, destino)
        cache = self.cache_dir / f"{chave}.json"

        if cache.exists():
            return json.loads(cache.read_text())["dist"]
        
        # 🔒 RATE LIMIT REAL (AQUI É O LUGAR CERTO)
        time.sleep(self.tempo_espera)

        payload = {
            "coordinates": [
                [origem[1], origem[0]],
                [destino[1], destino[0]],
            ]
        }

        resp = requests.post(
            "https://api.openrouteservice.org/v2/directions/driving-car",
            json=payload,
            headers={"Authorization": self.ors_api_key},
            timeout=30,
        )

        if resp.status_code != 200:
            raise RuntimeError(
                f"Erro ORS {resp.status_code}: {resp.text[:300]}"
            )


        data = resp.json()
        dist = data["routes"][0]["summary"]["distance"]
        cache.write_text(json.dumps({"dist": dist}))
        return dist

    def _parse_coord(self, valor):
        if pd.isna(valor):
            return None
        try:
            lat, lon = str(valor).split(",", 1)
            return float(lat.strip()), float(lon.strip())
        except Exception:
            return None

    def _validar_colunas(self, df):
        obrigatorias = {"CASA VEND", "DISTRIBUIDOR", "1ºCLIENTE"}
        if not obrigatorias.issubset(df.columns):
            raise ValueError("Excel não contém colunas obrigatórias")
        return df

    def _cache_key(self, o, d):
        return hashlib.md5(f"{o}-{d}".encode()).hexdigest()

    def _gerar_hash_registro(self, r):
        base = (
            f"{r.get('cod_vendedor')}|"
            f"{r.get('dia')}|"
            f"{r.get('dist_casa_cli')}|"
            f"{r.get('dist_casa_dist_cli')}"
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _falha(self, linha, origem, destino, motivo):
        msg = f"❌ Linha {linha}: {origem} → {destino} | {motivo}"
        self._log(msg)
        self._emit("falha", {
            "linha": linha,
            "origem": origem,
            "destino": destino,
            "motivo": motivo
        })
        if self.on_fail:
            self.on_fail(
                linha=linha,
                origem=origem,
                destino=destino,
                motivo=motivo
            )
