import customtkinter as ctk
from customtkinter import CTkImage
import os
import math
import time
import sys
from PIL import Image
def resource_path(relative_path: str) -> str:
    """
    Resolve caminho absoluto para recursos,
    funcionando em desenvolvimento e com PyInstaller.
    """
    try:
        # PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Raiz do projeto: componentes -> ui -> raiz
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

    return os.path.join(base_path, relative_path)


class LogoAnimator(ctk.CTkLabel):
    def __init__(self, master, image_path, size=120, bg="#ffffff"):
        super().__init__(
            master,
            fg_color=bg,
            text=""   # 🔥 mata o "CTkLabel" na raiz
        )


        abs_path = resource_path(image_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Logo não encontrado: {abs_path}")

        img = Image.open(abs_path).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)

        self.original = img
        self.tk_img = CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        self.configure(image=self.tk_img)

        self.angle = 0
        self._running = False
        self._job = None

    # ============================
    # Animações
    # ============================
    def rotate(self, fast=False):
        self.stop()
        self._running = True
        speed = 20 if fast else 10

        def _loop():
            if not self._running:
                return

            self.angle = (self.angle + speed) % 360
            rotated = self.original.rotate(
                self.angle, resample=Image.BICUBIC
            )
            self.tk_img = CTkImage(light_image=rotated, dark_image=rotated, size=(rotated.width, rotated.height))
            self.configure(image=self.tk_img)
            self._job = self.after(50, _loop)

        _loop()

    def pulse(self):
        self.stop()
        self._running = True
        start = time.time()

        def _loop():
            if not self._running:
                return

            t = time.time() - start
            scale = 1 + 0.05 * math.sin(t * 4)
            size = int(self.original.width * scale)

            img = self.original.resize(
                (size, size), Image.LANCZOS
            )
            self.tk_img = CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.configure(image=self.tk_img)
            self._job = self.after(50, _loop)

        _loop()

    def stop(self):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
            self._job = None