import customtkinter as ctk
# ui/layout/footer.py


class Footer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", height=30)
        self.pack(side="bottom", fill="x")

        ctk.CTkLabel(
            self,
            text="© 2025 PrimeiroKM - Manra Sistemas",
            font=("Arial", 11),
            text_color="gray"
        ).pack(side="left", padx=10)
