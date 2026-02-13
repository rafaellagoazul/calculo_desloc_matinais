import customtkinter as ctk
import subprocess
import sys
import threading
from pathlib import Path
from datetime import datetime

from tools.hub_lock import acquire_lock, release_lock

ERROR_LOG = Path("tools/runner/last_error.log")
HISTORY_LOG = Path("tools/runner/run_history.log")

_process: subprocess.Popen | None = None


def mount_main_runner(parent):
    ui = MainRunnerUI(parent)
    ui.pack(fill="both", expand=True)
    return ui


class MainRunnerUI(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.has_error = False
        self._build_ui()
        self._load_last_error()
        self._load_history()

    # ---------- UI ----------
    def _build_ui(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True)

        self.tab_run = self.tabs.add("Execução")
        self.tab_history = self.tabs.add("Histórico")

        self._build_run_tab()
        self._build_history_tab()

    def _build_run_tab(self):
        top = ctk.CTkFrame(self.tab_run)
        top.pack(fill="x", pady=5)

        self.status = ctk.CTkLabel(top, text="⚪ Parado")
        self.status.pack(side="left", padx=10)

        self.run_btn = ctk.CTkButton(
            top,
            text="▶ Executar Sistema",
            command=self.start
        )
        self.run_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            top,
            text="⏹ Parar",
            command=self.stop
        ).pack(side="left", padx=5)

        self.log = ctk.CTkTextbox(self.tab_run, height=160)
        self.log.pack(fill="x", padx=10, pady=10)
        self.log.configure(state="disabled")

    def _build_history_tab(self):
        self.history = ctk.CTkTextbox(self.tab_history)
        self.history.pack(fill="both", expand=True, padx=10, pady=10)
        self.history.configure(state="disabled")

    # ---------- PROCESS ----------
    def start(self):
        global _process
        if _process is not None:
            return

        if not acquire_lock("MainRunner"):
            self._append_log("❌ Outra ferramenta está em execução.\n")
            return

        self._clear_log()
        self._set_status("🟢 Rodando")
        self._log_history("START")

        _process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=Path.cwd(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        threading.Thread(
            target=self._monitor_process,
            daemon=True
        ).start()

    def stop(self):
        global _process
        if _process:
            _process.terminate()
            _process = None
            release_lock()
            self._set_status("⚪ Parado")
            self._log_history("STOP")
            self._load_history()

    def _monitor_process(self):
        global _process
        proc = _process
        if not proc:
            return

        stderr = proc.stderr.read() if proc.stderr else ""
        proc.wait()

        if proc.returncode == 0:
            self.after(0, self._set_status, "⚪ Parado")
            self._log_history("OK")
        else:
            self.after(0, self._set_error_state, stderr)
            self._log_history("ERROR")

        release_lock()
        self.after(0, self._load_history)
        _process = None

    # ---------- ERROR ----------
    def _set_error_state(self, error_text: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_error = f"[{ts}]\n{error_text}"

        self.has_error = True
        self._set_status("🔴 Erro")
        self._append_log(full_error)

        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        ERROR_LOG.write_text(full_error, encoding="utf-8")

    def _load_last_error(self):
        if ERROR_LOG.exists():
            self._append_log(ERROR_LOG.read_text(encoding="utf-8"))
            self._set_status("🔴 Erro")

    # ---------- HISTORY ----------
    def _log_history(self, event: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        HISTORY_LOG.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {event}\n")

    def _load_history(self):
        self.history.configure(state="normal")
        self.history.delete("1.0", "end")
        if HISTORY_LOG.exists():
            self.history.insert("end", HISTORY_LOG.read_text(encoding="utf-8"))
        self.history.configure(state="disabled")

    # ---------- UI HELPERS ----------
    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_status(self, text):
        self.status.configure(text=text)
