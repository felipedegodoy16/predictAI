import requests
import time
import random
import json

# URL do Webhook na aplicação (endpoint criado para receber os dados em massa)
WEBHOOK_URL = "http://127.0.0.9:8000/api/sensors/readings/bulk/"
# Nota: Usamos 127.0.0.9:8000 conforme configurações locais da sua máquina, mas pode ser localhost.

# IDs dos sensores que a máquina possui (ajuste conforme os sensores criados no banco)
SENSOR_IDS = [1, 2, 3, 4, 5, 6]

def gerar_dados_maquina():
    """Gera dados simulados para cada sensor da máquina."""
    readings = []
    
    for sensor_id in SENSOR_IDS:
        # Simulando valores baseados no ID do sensor para parecerem reais
        if sensor_id == 1: # Temperatura
            valor = round(random.uniform(60.0, 95.0), 2)
        elif sensor_id == 3: # Vibração
            valor = round(random.uniform(0.5, 6.0), 2)
        else:
            valor = round(random.uniform(10.0, 50.0), 2)
            
        readings.append({
            "sensor": sensor_id,
            "value": valor
        })
        
    return {"readings": readings}

def simular_envio_continuo(intervalo_segundos=5):
    """Envia dados para o webhook continuamente a cada N segundos."""
    print("🚀 Iniciando simulador da Máquina (Webhook Client)...")
    print(f"📡 Enviando dados para: {WEBHOOK_URL}\n")
    
    while True:
        payload = gerar_dados_maquina()
        
        try:
            # Enviando o POST request (Webhook) para a aplicação
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            
            agora = time.strftime("%H:%M:%S")
            if response.status_code in [200, 201]:
                dados_retorno = response.json()
                print(f"[{agora}] ✅ Sucesso! {dados_retorno.get('created', 0)} leituras enviadas. "
                      f"Alertas: {dados_retorno.get('alerts_generated', 0)}")
            else:
                print(f"[{agora}] ❌ Erro na API (Status {response.status_code}): {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"[{agora}] ⚠️ Falha de conexão com o servidor. A aplicação está rodando? Erro: {e}")
            
        # Aguarda o intervalo antes de enviar a próxima leitura
        time.sleep(intervalo_segundos)

if __name__ == "__main__":
    # Para testar, certifique-se de que o backend (manage.py runserver) esteja rodando.
    simular_envio_continuo(intervalo_segundos=3)
