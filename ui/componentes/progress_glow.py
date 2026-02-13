import math


class ProgressGlow:
    def __init__(self, master, progress_bar):
        self.master = master
        self.progress = progress_bar

        self._jobs = []
        self._running = False

        self._glows = []
        self._phases = [0.0, 0.5]  # dois brilhos defasados

        self._min_visual = 0.15  # nunca menos que 15%

        self._criar_glows()

    # ───────────────────────────────────────

    def _criar_glows(self):
        for cor in ("#93c5fd", "#60a5fa"):
            glow = self.master.__class__(
                self.master,
                height=6,
                width=70,
                fg_color=cor,
                corner_radius=6
            )
            glow.place_forget()
            self._glows.append(glow)

    # ───────────────────────────────────────

    def start(self):
        if self._running:
            return

        self._running = True

        for i in range(2):
            self._animar(i)

    def stop(self):
        self._running = False
        for job in self._jobs:
            try:
                self.master.after_cancel(job)
            except Exception:
                pass
        self._jobs.clear()

        for g in self._glows:
            g.place_forget()

    # ───────────────────────────────────────

    def _animar(self, idx):
        phase = self._phases[idx]
        glow = self._glows[idx]

        glow.place(relx=0, rely=0.5, anchor="w")

        def loop():
            if not self._running:
                return

            progresso = float(self.progress.get())

            # limite visual inteligente
            limite = max(self._min_visual, progresso)

            # easing senoidal
            phase_local = (phase + loop.t) % 1.0
            eased = 0.5 - 0.5 * math.cos(phase_local * math.pi * 2)

            x = eased * limite

            glow.place(relx=x, rely=0.5, anchor="w")

            loop.t += 0.015
            job = self.master.after(30, loop)
            self._jobs.append(job)

        loop.t = 0
        loop()