import customtkinter as ctk
from pathlib import Path
import threading
import io
import contextlib
import traceback
import time
import shutil
import builtins

from tools.explorer.explorer_state import ExplorerState

# ───────────────── PATHS ─────────────────
ROOT = Path(__file__).resolve().parents[2]
BACKUP_DIR = ROOT / ".backups_code_fixer"

state = ExplorerState()


class CodeFixerApp(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self._build_ui()
        self._configure_tags()

    # ───────── UI ─────────
    def _build_ui(self):
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(body, text="📄 Script de Correção").grid(row=0, column=0, sticky="w")
        self.code_box = ctk.CTkTextbox(body, wrap="none")
        self.code_box.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(body, text="🧾 Log").grid(row=0, column=1, sticky="w")
        self.log_box = ctk.CTkTextbox(body, wrap="word")
        self.log_box.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        ctk.CTkButton(
            body,
            text="⚡ Executar Script",
            command=self.run_script
        ).grid(row=2, column=0, pady=10, sticky="w")

    # ───────── LOG ─────────
    def _configure_tags(self):
        self.log_box.tag_config("ok", foreground="#1dd1a1")
        self.log_box.tag_config("error", foreground="#ff5f5f")
        self.log_box.tag_config("trace", foreground="#ff9f43")

    def _log(self, text, tag=None):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ───────── FIXER CORE ─────────
    def run_script(self):
        code = self.code_box.get("1.0", "end").strip()
        if not code:
            return

        class LogWriter(io.StringIO):
            def __init__(self, log_func):
                super().__init__()
                self.log_func = log_func

            def write(self, s: str) -> int:
                if s.strip():
                    self.log_func(s.rstrip())
                return len(s)

        def exec_script():
            original_open = builtins.open

            def safe_open(file, mode="r", *a, **k):
                if any(m in mode for m in ("w", "a", "x")):
                    try:
                        rel = str(Path(file).resolve().relative_to(ROOT))
                        if state.is_frozen(rel):
                            raise PermissionError(f"⛔ Arquivo congelado: {rel}")
                    except ValueError:
                        pass
                return original_open(file, mode, *a, **k)

            try:
                builtins.open = safe_open

                ctx = {"ROOT": ROOT}
                writer = LogWriter(self._log)

                with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                    exec(code, ctx)

                if "ARQ" not in ctx or not isinstance(ctx["ARQ"], Path):
                    raise RuntimeError("Script deve definir ARQ = Path(...)")

                arq: Path = ctx["ARQ"]

                BACKUP_DIR.mkdir(exist_ok=True)
                backup = BACKUP_DIR / f"{arq.name}.{int(time.time())}.bak"
                shutil.copy2(arq, backup)

                self._log(f"💾 Backup criado: {backup}", "ok")
                self._log(f"✔ Correção aplicada em {arq}", "ok")

            except Exception:
                for line in traceback.format_exc().splitlines():
                    self._log(line, "trace")

            finally:
                builtins.open = original_open

        threading.Thread(target=exec_script, daemon=True).start()


def mount_code_fixer_tool(parent):
    ui = CodeFixerApp(parent)
    ui.pack(fill="both", expand=True)
    return ui
