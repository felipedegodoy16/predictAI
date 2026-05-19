# Machine Simulator — PredictAI

Simula uma máquina industrial enviando dados de sensores para a API do PredictAI.

## Como usar

1. **Instale a dependência** (apenas `requests` — `tkinter` já vem com o Python):
   ```
   pip install requests
   ```

2. **Configure** o arquivo `config.py`:
   - `API_BASE_URL`: URL do backend Django (padrão `http://localhost:8000`)
   - `DEFAULT_MACHINE_ID`: ID da máquina cadastrada no PredictAI
   - `DEFAULT_SENSORS`: sensores padrão (chaves = IDs reais no banco)

3. **Execute**:
   ```
   python simulator.py
   ```
   Ou dê dois cliques em **`run.bat`**.

## Interface

| Elemento | Descrição |
|---|---|
| **Buscar Sensores** | Consulta a API e carrega os sensores da máquina |
| **Modo Normal / Alerta / Crítico** | Define o intervalo de geração de cada sensor |
| **Valor Manual** | Fixa um valor específico para um sensor |
| **Cenário** | Aplica um perfil de falha a todos os sensores de uma vez |
| **▶ Iniciar / ⏹ Parar** | Controla o envio periódico de leituras |
| **Intervalo (s)** | Segundos entre cada envio em lote |

## Fluxo de dados

```
Simulator ──bulk POST /api/sensors/readings/bulk/──▶ Django
                                                      │
                                            SensorReadingCreateView
                                                      │
                                              _check_and_create_alert()
                                                      │
                                             Alert criado no banco
                                                      │
                                          Frontend PredictAI exibe alerta
```

## Sensores simulados (padrão)

| ID | Nome | Unidade |
|---|---|---|
| 1 | Temperatura Motor | °C |
| 2 | Temperatura Rolamento | °C |
| 3 | Vibração Eixo X | mm/s |
| 4 | Vibração Eixo Y | mm/s |
| 5 | Pressão Hidráulica | bar |
| 6 | Corrente Elétrica | A |
