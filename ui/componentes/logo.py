import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Resolve caminho absoluto para recursos,
    compatível com desenvolvimento e PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
    return os.path.join(base_path, relative_path)


class Logo(ctk.CTkLabel):
    def __init__(self, master, image_path, height=48, bg="transparent"):
        abs_path = resource_path(image_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Logo não encontrado: {abs_path}")

        img = Image.open(abs_path).convert("RGBA")

        ratio = img.width / img.height
        width = int(height * ratio)

        self.ctk_img = CTkImage(
            light_image=img,
            dark_image=img,
            size=(width, height)
        )

        super().__init__(
            master,
            image=self.ctk_img,
            fg_color=bg
        )

        # 🔥 ESSENCIAL para evitar o texto "CTkLabel"
        self.configure(text="")
