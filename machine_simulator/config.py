# ──────────────────────────────────────────────────────────────
#  CONFIGURAÇÃO DO SIMULADOR
#  Ajuste aqui os IDs que batem com o seu banco de dados.
# ──────────────────────────────────────────────────────────────

# URL base da API do PredictAI
API_BASE_URL = "http://localhost:8000"

# ID da máquina cadastrada no PredictAI (altere conforme o seu banco)
DEFAULT_MACHINE_ID = 1

# ──────────────────────────────────────────────────────────────
# Sensores padrão (chave = sensor_id no banco)
# Se você buscar via "🔍 Buscar Sensores" os IDs são preenchidos
# automaticamente. Estes valores servem como fallback/demo.
# ──────────────────────────────────────────────────────────────
# Estrutura de cada sensor:
#   name           – rótulo exibido
#   unit           – unidade de medida
#   normal_range   – [min, max] para modo Normal
#   warning_range  – [min, max] para modo Alerta
#   critical_range – [min, max] para modo Crítico
# ──────────────────────────────────────────────────────────────

DEFAULT_SENSORS: dict = {
    # ── Temperatura ───────────────────────────────────────────
    "1": {
        "name":          "Temperatura Motor",
        "unit":          "°C",
        "normal_range":  [60.0,  80.0],
        "warning_range": [80.0,  95.0],
        "critical_range":[95.0, 130.0],
    },
    "2": {
        "name":          "Temperatura Rolamento",
        "unit":          "°C",
        "normal_range":  [40.0,  65.0],
        "warning_range": [65.0,  80.0],
        "critical_range":[80.0, 110.0],
    },

    # ── Vibração ──────────────────────────────────────────────
    "3": {
        "name":          "Vibração Eixo X",
        "unit":          "mm/s",
        "normal_range":  [0.5,  3.0],
        "warning_range": [3.0,  5.5],
        "critical_range":[5.5, 10.0],
    },
    "4": {
        "name":          "Vibração Eixo Y",
        "unit":          "mm/s",
        "normal_range":  [0.5,  3.0],
        "warning_range": [3.0,  5.5],
        "critical_range":[5.5, 10.0],
    },

    # ── Pressão ───────────────────────────────────────────────
    "5": {
        "name":          "Pressão Hidráulica",
        "unit":          "bar",
        "normal_range":  [40.0,  60.0],
        "warning_range": [60.0,  75.0],
        "critical_range":[75.0, 100.0],
    },

    # ── Corrente ──────────────────────────────────────────────
    "6": {
        "name":          "Corrente Elétrica",
        "unit":          "A",
        "normal_range":  [10.0, 25.0],
        "warning_range": [25.0, 35.0],
        "critical_range":[35.0, 50.0],
    },
}

# ──────────────────────────────────────────────────────────────
# Cenários pré-definidos
# Chave = nome exibido no combo; Valor = dict {sensor_id: modo}
# Modos aceitos: "normal" | "warning" | "critical"
# Sensores não listados permanecem no modo atual.
# ──────────────────────────────────────────────────────────────
SENSOR_SCENARIOS: dict = {
    "✅ Operação Normal": {
        "1": "normal", "2": "normal",
        "3": "normal", "4": "normal",
        "5": "normal", "6": "normal",
    },
    "🌡️ Superaquecimento": {
        "1": "critical",
        "2": "warning",
        "3": "normal",
        "4": "normal",
        "5": "normal",
        "6": "warning",
    },
    "⚡ Sobrecarga Elétrica": {
        "1": "warning",
        "2": "normal",
        "3": "normal",
        "4": "normal",
        "5": "normal",
        "6": "critical",
    },
    "📳 Vibração Excessiva": {
        "1": "normal",
        "2": "warning",
        "3": "critical",
        "4": "critical",
        "5": "normal",
        "6": "normal",
    },
    "💧 Falha Hidráulica": {
        "1": "normal",
        "2": "normal",
        "3": "warning",
        "4": "normal",
        "5": "critical",
        "6": "normal",
    },
    "🔥 Falha Geral Crítica": {
        "1": "critical",
        "2": "critical",
        "3": "critical",
        "4": "critical",
        "5": "critical",
        "6": "critical",
    },
}
