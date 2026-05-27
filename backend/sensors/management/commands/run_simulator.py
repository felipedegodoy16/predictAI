import time
import random
import requests
from django.core.management.base import BaseCommand
from machines.models import Machine
from sensors.models import Sensor

class Command(BaseCommand):
    help = 'Roda o simulador dinâmico, buscando máquinas e sensores do banco de dados e enviando leituras via Webhook'

    def handle(self, *args, **options):
        # A URL padrão do Webhook local
        WEBHOOK_URL = "http://127.0.0.9:8000/api/sensors/readings/bulk/"
        INTERVAL = 5  # Em segundos, conforme solicitado
        
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando simulador dinâmico de Máquinas e Sensores...'))
        self.stdout.write(f'📡 Webhook alvo: {WEBHOOK_URL}')
        self.stdout.write(f'⏱️  Frequência: a cada {INTERVAL} segundos\n')
        
        while True:
            # Busca todas as máquinas do banco de dados no momento exato (dinâmico)
            machines = Machine.objects.prefetch_related('sensors').all()
            if not machines.exists():
                self.stdout.write(self.style.WARNING('Nenhuma máquina cadastrada no banco. Aguardando...'))
                time.sleep(INTERVAL)
                continue
                
            readings = []
            
            for machine in machines:
                # Varre os sensores de cada máquina
                for sensor in machine.sensors.filter(is_active=True):
                    # Identifica os limites para basear a geração
                    min_val = float(sensor.min_limit) if sensor.min_limit is not None else 0.0
                    max_val = float(sensor.limit_temp) if sensor.limit_temp is not None else (min_val + 100.0)
                    
                    if max_val <= min_val:
                        max_val = min_val + 50.0
                        
                    # Gerar valor: a maioria das vezes "Normal", mas com pequenas chances de anomalias
                    anomaly_chance = random.random()
                    
                    if anomaly_chance < 0.05:
                        # 5% de chance de cair ABAIXO do limite mínimo esperado (Gera OS Automática)
                        val = min_val - random.uniform(1.0, 10.0)
                    elif anomaly_chance > 0.95:
                        # 5% de chance de subir ACIMA do limite máximo (Gera OS Automática)
                        val = max_val + random.uniform(1.0, 10.0)
                    else:
                        # 90% das vezes opera dentro do limite esperado
                        val = random.uniform(min_val, max_val)
                        
                    readings.append({
                        "sensor": sensor.id,
                        "value": round(val, 2)
                    })
                    
            if not readings:
                self.stdout.write(self.style.WARNING('Nenhum sensor ativo encontrado nas máquinas. Aguardando...'))
                time.sleep(INTERVAL)
                continue
                
            payload = {"readings": readings}
            
            try:
                # Envia via POST (Webhook HTTP real)
                response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
                agora = time.strftime("%H:%M:%S")
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.stdout.write(self.style.SUCCESS(
                        f"[{agora}] ✅ Sucesso! Máquinas processadas: {machines.count()} | Leituras enviadas: {len(readings)} | "
                        f"Alertas: {data.get('alerts_generated', 0)} | OS geradas: {data.get('work_orders_created', 0)}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(f"[{agora}] ❌ Erro API: {response.status_code} - {response.text}"))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"[{agora}] ⚠️ Falha na conexão com {WEBHOOK_URL}. O backend (runserver) está rodando em outro terminal?"))
                
            # Aguarda o intervalo e envia de novo
            time.sleep(INTERVAL)
