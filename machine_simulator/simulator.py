import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random
import math
import requests
import json
from datetime import datetime
from config import API_BASE_URL, DEFAULT_MACHINE_ID, DEFAULT_SENSORS, SENSOR_SCENARIOS

# ─────────────────────────────────────────────
# Paleta de cores
# ─────────────────────────────────────────────
BG       = "#0d1117"
PANEL    = "#161b22"
CARD     = "#1c2128"
BORDER   = "#30363d"
ACCENT   = "#58a6ff"
GREEN    = "#3fb950"
YELLOW   = "#d29922"
RED      = "#f85149"
TEXT     = "#e6edf3"
SUBTEXT  = "#8b949e"
FONT     = "Segoe UI"


class SensorCard(tk.Frame):
    """Card visual para um sensor individual."""

    def __init__(self, parent, sensor_id, sensor_info, **kwargs):
        super().__init__(parent, bg=CARD, relief="flat", **kwargs)
        self.sensor_id   = sensor_id
        self.sensor_info = sensor_info
        self.value       = sensor_info["normal_range"][0]
        self.mode        = "normal"   # normal | warning | critical | manual
        self.manual_val  = tk.DoubleVar(value=self.value)

        self._build()

    def _build(self):
        # Cabeçalho
        hdr = tk.Frame(self, bg=CARD)
        hdr.pack(fill="x", padx=12, pady=(10, 4))

        self.status_dot = tk.Label(hdr, text="●", fg=GREEN, bg=CARD,
                                   font=(FONT, 10))
        self.status_dot.pack(side="left")

        tk.Label(hdr, text=self.sensor_info["name"], fg=TEXT, bg=CARD,
                 font=(FONT, 11, "bold")).pack(side="left", padx=6)

        tk.Label(hdr, text=f"[{self.sensor_info['unit']}]", fg=SUBTEXT,
                 bg=CARD, font=(FONT, 9)).pack(side="left")

        # Valor atual
        self.value_lbl = tk.Label(self, text="---", fg=ACCENT, bg=CARD,
                                  font=(FONT, 28, "bold"))
        self.value_lbl.pack(pady=4)

        # Barra de progresso
        self.bar = ttk.Progressbar(self, orient="horizontal",
                                   length=180, mode="determinate")
        self.bar.pack(pady=2)

        # Modo selector
        mode_frame = tk.Frame(self, bg=CARD)
        mode_frame.pack(pady=(8, 4))

        for label, mode, color in [("Normal", "normal", GREEN),
                                   ("Alerta",  "warning",  YELLOW),
                                   ("Crítico", "critical", RED)]:
            btn = tk.Button(mode_frame, text=label, fg="white", bg=BORDER,
                            activebackground=color, font=(FONT, 8),
                            relief="flat", cursor="hand2", width=7,
                            command=lambda m=mode: self.set_mode(m))
            btn.pack(side="left", padx=2)

        # Controle manual
        manual_frame = tk.Frame(self, bg=CARD)
        manual_frame.pack(pady=(4, 10))

        tk.Label(manual_frame, text="Manual:", fg=SUBTEXT, bg=CARD,
                 font=(FONT, 8)).pack(side="left")

        self.manual_entry = tk.Entry(manual_frame, textvariable=self.manual_val,
                                     width=8, bg=PANEL, fg=TEXT,
                                     insertbackground=TEXT, relief="flat",
                                     font=(FONT, 9))
        self.manual_entry.pack(side="left", padx=4)

        tk.Button(manual_frame, text="Definir", fg="white", bg=ACCENT,
                  font=(FONT, 8), relief="flat", cursor="hand2",
                  command=self._set_manual).pack(side="left")

    def set_mode(self, mode):
        self.mode = mode

    def _set_manual(self):
        try:
            v = float(self.manual_val.get())
            self.value = v
            self.mode  = "manual"
            self._update_display(v)
        except ValueError:
            pass

    def next_value(self):
        """Gera próximo valor de acordo com o modo ativo."""
        lo, hi = self.sensor_info["normal_range"]
        wl, wh = self.sensor_info["warning_range"]
        cl, ch = self.sensor_info["critical_range"]

        if self.mode == "manual":
            v = self.value
        elif self.mode == "normal":
            v = random.uniform(lo, hi)
            v += math.sin(time.time() * 0.3) * (hi - lo) * 0.05
        elif self.mode == "warning":
            v = random.uniform(wl, wh)
        elif self.mode == "critical":
            v = random.uniform(cl, ch)

        self.value = round(v, 2)
        self._update_display(self.value)
        return self.value

    def _update_display(self, v):
        lo, hi = self.sensor_info["normal_range"]
        _, wh  = self.sensor_info["warning_range"]
        _, ch  = self.sensor_info["critical_range"]

        self.value_lbl.config(text=f"{v:.2f}")

        # Cor baseada no valor
        if self.mode == "critical" or v >= wh:
            color = RED
        elif self.mode == "warning" or v >= lo + (hi - lo) * 0.8:
            color = YELLOW
        else:
            color = GREEN

        self.value_lbl.config(fg=color)
        self.status_dot.config(fg=color)

        # Barra
        span = ch - lo
        pct  = min(100, max(0, (v - lo) / span * 100)) if span else 0
        self.bar["value"] = pct


class SimulatorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("🏭 PredictAI — Machine Simulator")
        self.configure(bg=BG)
        self.geometry("1100x780")
        self.resizable(True, True)

        self.machine_id  = tk.StringVar(value=str(DEFAULT_MACHINE_ID))
        self.api_url     = tk.StringVar(value=API_BASE_URL)
        self.interval    = tk.IntVar(value=3)
        self.running     = False
        self._thread     = None
        self.sensor_cards: dict[str, SensorCard] = {}

        self._build_ui()
        self._update_clock()

    # ─── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ──────────────────────────────
        top = tk.Frame(self, bg=PANEL, height=60)
        top.pack(fill="x")

        tk.Label(top, text="🏭", font=(FONT, 20), bg=PANEL, fg=ACCENT).pack(
            side="left", padx=(16, 4), pady=10)
        tk.Label(top, text="PredictAI  Machine Simulator", fg=TEXT, bg=PANEL,
                 font=(FONT, 16, "bold")).pack(side="left", pady=10)

        self.clock_lbl = tk.Label(top, text="", fg=SUBTEXT, bg=PANEL,
                                  font=(FONT, 10))
        self.clock_lbl.pack(side="right", padx=16)

        self.status_lbl = tk.Label(top, text="⏸ Parado", fg=YELLOW, bg=PANEL,
                                   font=(FONT, 11, "bold"))
        self.status_lbl.pack(side="right", padx=16)

        # ── Config bar ───────────────────────────
        cfg = tk.Frame(self, bg=CARD, pady=8)
        cfg.pack(fill="x", padx=0)

        def lbl(txt): return tk.Label(cfg, text=txt, fg=SUBTEXT, bg=CARD,
                                      font=(FONT, 9))
        def ent(var, w=30): return tk.Entry(cfg, textvariable=var, width=w,
                                            bg=PANEL, fg=TEXT, relief="flat",
                                            insertbackground=TEXT,
                                            font=(FONT, 9))

        lbl("URL da API:").pack(side="left", padx=(16, 2))
        ent(self.api_url, 40).pack(side="left")
        lbl("  Machine ID:").pack(side="left", padx=(12, 2))
        ent(self.machine_id, 10).pack(side="left")
        lbl("  Intervalo (s):").pack(side="left", padx=(12, 2))
        ent(self.interval, 4).pack(side="left")

        # Botão buscar sensores
        tk.Button(cfg, text="🔍 Buscar Sensores", fg="white", bg=BORDER,
                  font=(FONT, 9), relief="flat", cursor="hand2",
                  command=self._fetch_sensors).pack(side="left", padx=(16, 4))

        # Botões Start / Stop
        self.btn_start = tk.Button(cfg, text="▶ Iniciar", fg="white",
                                   bg=GREEN, font=(FONT, 9, "bold"),
                                   relief="flat", cursor="hand2",
                                   command=self.start_simulation)
        self.btn_start.pack(side="left", padx=4)

        self.btn_stop = tk.Button(cfg, text="⏹ Parar", fg="white", bg=RED,
                                  font=(FONT, 9, "bold"), relief="flat",
                                  cursor="hand2", state="disabled",
                                  command=self.stop_simulation)
        self.btn_stop.pack(side="left", padx=4)

        # Botão cenário
        tk.Label(cfg, text="  Cenário:", fg=SUBTEXT, bg=CARD,
                 font=(FONT, 9)).pack(side="left", padx=(12, 2))
        self.scenario_var = tk.StringVar(value=list(SENSOR_SCENARIOS.keys())[0])
        scenario_cb = ttk.Combobox(cfg, textvariable=self.scenario_var,
                                   values=list(SENSOR_SCENARIOS.keys()),
                                   state="readonly", width=18)
        scenario_cb.pack(side="left")
        tk.Button(cfg, text="Aplicar", fg="white", bg=ACCENT,
                  font=(FONT, 9), relief="flat", cursor="hand2",
                  command=self._apply_scenario).pack(side="left", padx=4)

        # ── Main area ────────────────────────────
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=12, pady=8)

        # Coluna esquerda — sensores
        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="SENSORES DA MÁQUINA", fg=SUBTEXT, bg=BG,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.sensor_frame = tk.Frame(left, bg=BG)
        self.sensor_frame.pack(fill="both", expand=True)

        # Coluna direita — log
        right = tk.Frame(main, bg=BG, width=320)
        right.pack(side="right", fill="both", padx=(12, 0))
        right.pack_propagate(False)

        tk.Label(right, text="LOG DE TRANSMISSÃO", fg=SUBTEXT, bg=BG,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.log_box = scrolledtext.ScrolledText(
            right, bg=PANEL, fg=TEXT, font=("Courier New", 9),
            relief="flat", state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True)

        self.log_box.tag_config("ok",   foreground=GREEN)
        self.log_box.tag_config("err",  foreground=RED)
        self.log_box.tag_config("warn", foreground=YELLOW)
        self.log_box.tag_config("info", foreground=ACCENT)

        # Barra inferior — stats
        bot = tk.Frame(self, bg=PANEL, height=32)
        bot.pack(fill="x", side="bottom")

        self.stat_sent  = tk.Label(bot, text="Enviados: 0", fg=TEXT, bg=PANEL,
                                   font=(FONT, 9))
        self.stat_sent.pack(side="left", padx=16)
        self.stat_err   = tk.Label(bot, text="Erros: 0", fg=RED, bg=PANEL,
                                   font=(FONT, 9))
        self.stat_err.pack(side="left", padx=12)
        self.stat_alerts= tk.Label(bot, text="Alertas gerados: 0", fg=YELLOW,
                                   bg=PANEL, font=(FONT, 9))
        self.stat_alerts.pack(side="left", padx=12)

        self._sent = 0
        self._errs = 0
        self._alerts = 0

        # Carregar sensores padrão
        self._load_default_sensors()

    # ─── Sensores ────────────────────────────────────────────────────────────

    def _load_default_sensors(self):
        """Carrega os sensores padrão definidos em config.py."""
        for widget in self.sensor_frame.winfo_children():
            widget.destroy()
        self.sensor_cards.clear()

        cols = 3
        for i, (sid, sinfo) in enumerate(DEFAULT_SENSORS.items()):
            card = SensorCard(self.sensor_frame, sid, sinfo,
                              width=220, height=230)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8,
                      sticky="nsew")
            self.sensor_cards[sid] = card

        for c in range(cols):
            self.sensor_frame.columnconfigure(c, weight=1)

        self._log(f"✔ {len(DEFAULT_SENSORS)} sensores padrão carregados",
                  "info")

    def _fetch_sensors(self):
        """Busca sensores da API para a machine_id informada."""
        mid = self.machine_id.get().strip()
        if not mid:
            messagebox.showwarning("Aviso", "Informe o Machine ID.")
            return
        url = f"{self.api_url.get().rstrip('/')}/api/sensors/?machine={mid}"
        self._log(f"🔍 Buscando sensores em {url}", "info")

        def _fetch():
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    results = data.get("results", data) if isinstance(data, dict) else data
                    self._log(f"✔ {len(results)} sensores encontrados na API",
                              "ok")
                    self.after(0, lambda: self._render_api_sensors(results))
                else:
                    self._log(f"✗ HTTP {r.status_code}: {r.text[:80]}", "err")
            except Exception as e:
                self._log(f"✗ Erro ao buscar: {e}", "err")

        threading.Thread(target=_fetch, daemon=True).start()

    def _render_api_sensors(self, sensors):
        """Renderiza cards com sensores vindos da API."""
        for widget in self.sensor_frame.winfo_children():
            widget.destroy()
        self.sensor_cards.clear()

        cols = 3
        for i, s in enumerate(sensors):
            sid = str(s["id"])
            # Mapear campos da API para o formato interno
            sinfo = {
                "name":         s.get("name") or s.get("sensor_type", f"Sensor {sid}"),
                "unit":         s.get("unit", ""),
                "normal_range": [0, float(s.get("limit_temp") or 100)],
                "warning_range":[float(s.get("limit_temp") or 100) * 0.8,
                                 float(s.get("limit_temp") or 100) * 0.95],
                "critical_range":[float(s.get("limit_temp") or 100) * 0.95,
                                  float(s.get("limit_temp") or 100) * 1.2],
            }
            card = SensorCard(self.sensor_frame, sid, sinfo,
                              width=220, height=230)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8,
                      sticky="nsew")
            self.sensor_cards[sid] = card

        for c in range(cols):
            self.sensor_frame.columnconfigure(c, weight=1)

    # ─── Cenários ────────────────────────────────────────────────────────────

    def _apply_scenario(self):
        scenario = SENSOR_SCENARIOS.get(self.scenario_var.get(), {})
        for sid, mode in scenario.items():
            if sid in self.sensor_cards:
                self.sensor_cards[sid].set_mode(mode)
        self._log(f"▶ Cenário aplicado: {self.scenario_var.get()}", "warn")

    # ─── Simulação ────────────────────────────────────────────────────────────

    def start_simulation(self):
        if self.running:
            return
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_lbl.config(text="▶ Transmitindo…", fg=GREEN)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._log("━━━ Simulação iniciada ━━━", "info")

    def stop_simulation(self):
        self.running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_lbl.config(text="⏸ Parado", fg=YELLOW)
        self._log("━━━ Simulação parada ━━━", "warn")

    def _loop(self):
        while self.running:
            self._send_readings()
            for _ in range(self.interval.get() * 10):
                if not self.running:
                    break
                time.sleep(0.1)

    def _send_readings(self):
        readings = []
        for sid, card in self.sensor_cards.items():
            v = card.next_value()
            readings.append({"sensor": int(sid), "value": v})

        url = f"{self.api_url.get().rstrip('/')}/api/sensors/readings/bulk/"
        payload = {"readings": readings}

        try:
            r = requests.post(url, json=payload, timeout=5)
            if r.status_code in (200, 201):
                data = r.json()
                created = data.get("created", len(readings))
                alerts  = data.get("alerts_generated", 0)
                self._sent   += created
                self._alerts += alerts
                ts = datetime.now().strftime("%H:%M:%S")
                self._log(
                    f"[{ts}] ✔ {created} leituras enviadas"
                    + (f" | ⚠ {alerts} alertas" if alerts else ""),
                    "ok" if not alerts else "warn"
                )
                self.after(0, self._update_stats)
            else:
                self._errs += 1
                self._log(
                    f"✗ HTTP {r.status_code}: {r.text[:120]}", "err")
                self.after(0, self._update_stats)
        except Exception as e:
            self._errs += 1
            self._log(f"✗ Conexão: {e}", "err")
            self.after(0, self._update_stats)

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def _log(self, msg, tag=""):
        def _do():
            self.log_box.config(state="normal")
            self.log_box.insert("end", msg + "\n", tag)
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.after(0, _do)

    def _update_stats(self):
        self.stat_sent.config(text=f"Enviados: {self._sent}")
        self.stat_err.config(text=f"Erros: {self._errs}")
        self.stat_alerts.config(text=f"Alertas gerados: {self._alerts}")

    def _update_clock(self):
        self.clock_lbl.config(
            text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.after(1000, self._update_clock)


if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()
