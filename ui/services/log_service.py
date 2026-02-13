class LogService:
    def __init__(self, app):
        self.app = app

    # =========================
    # API PÚBLICA
    # =========================
    def info(self, msg, contexto=None):
        self._write("log_box", "INFO", msg, contexto)

    def error(self, msg, contexto=None):
        self._write("log_box", "ERROR", msg, contexto)

    def debug(self, msg):
        self._write("debug_box", "DEBUG", msg)

    # =========================
    # CORE
    # =========================
    def _write(self, attr_name, level, msg, contexto=None):
        textbox = getattr(self.app, attr_name, None)
        if not textbox:
            return  # UI ainda não pronta

        if contexto:
            msg = f"[{contexto}] {msg}"

        linha = f"{level}: {msg}"

        def _do():
            textbox.configure(state="normal")
            textbox.insert("end", linha + "\n")
            textbox.see("end")
            textbox.configure(state="disabled")

        self.app.after(0, _do)