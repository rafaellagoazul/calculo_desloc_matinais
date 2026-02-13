# ui/services/thread_service.py
import threading
import traceback


class ThreadService:
    def __init__(self, app):
        self.app = app

    def run_safe(self, target, on_error=None, on_finally=None):
        def _runner():
            try:
                target()
            except Exception as e:
                tb = traceback.format_exc()

                def _handle_error():
                    # LOG VISUAL
                    if hasattr(self.app, "logger"):
                        self.app.logger.error(str(e), "THREAD")
                        self.app.logger.debug(tb)

                    # CALLBACK EXTERNO
                    if on_error:
                        on_error(e)

                    # ESTADO VISUAL
                    if hasattr(self.app, "estado_erro"):
                        self.app.estado_erro()

                self.app.after(0, _handle_error)

            finally:
                if on_finally:
                    self.app.after(0, on_finally)

        threading.Thread(
            target=_runner,
            daemon=True
        ).start()