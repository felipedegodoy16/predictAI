import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from sensors.models import Sensor, SensorReading
from alerts.models import Alert
from alerts.services import get_risk_level, get_recommendation


class Command(BaseCommand):
    help = 'Gera leituras historicas de sensores com anomalias controladas (30 dias)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Numero de dias de historico a gerar (padrao: 30)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Intervalo em minutos entre leituras (padrao: 15)',
        )
        parser.add_argument(
            '--anomaly-rate',
            type=float,
            default=0.05,
            help='Taxa de anomalias (0.0 a 1.0, padrao: 0.05)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove todas as leituras e alertas existentes antes de gerar novos.',
        )

    def handle(self, *args, **options):
        days = options['days']
        interval_minutes = options['interval']
        anomaly_rate = options['anomaly_rate']

        if options['reset']:
            Alert.objects.all().delete()
            count, _ = SensorReading.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removidas {count} leituras e alertas existentes.'))

        sensors = list(Sensor.objects.filter(is_active=True).select_related('machine'))
        if not sensors:
            self.stdout.write(self.style.ERROR(
                'Nenhum sensor ativo encontrado. Execute seed_machines primeiro.'
            ))
            return

        self.stdout.write(f'Gerando leituras para {len(sensors)} sensor(es) em {days} dia(s)...')

        now = timezone.now()
        start = now - timedelta(days=days)
        total_readings = 0
        total_anomalies = 0
        total_alerts = 0

        readings_to_create = []

        for sensor in sensors:
            current = start
            min_t = float(sensor.min_threshold) if sensor.min_threshold is not None else None
            max_t = float(sensor.max_threshold) if sensor.max_threshold is not None else None

            # Determine base value range
            if min_t is not None and max_t is not None:
                normal_min = min_t + (max_t - min_t) * 0.2
                normal_max = max_t - (max_t - min_t) * 0.2
            elif min_t is not None:
                normal_min = min_t
                normal_max = min_t * 3
            elif max_t is not None:
                normal_min = max_t * 0.3
                normal_max = max_t * 0.8
            else:
                normal_min = 0
                normal_max = 100

            while current <= now:
                is_anomaly_forced = random.random() < anomaly_rate

                if is_anomaly_forced and min_t is not None and max_t is not None:
                    # Generate value outside thresholds
                    if random.random() > 0.5:
                        value = round(max_t * (1 + random.uniform(0.1, 0.5)), 4)
                    else:
                        value = round(min_t * max(0.1, (1 - random.uniform(0.1, 0.5))), 4)
                else:
                    # Generate normal value with some noise
                    value = round(random.uniform(normal_min, normal_max), 4)
                    # Add a slight drift over time (simulate degradation near end)
                    days_since_start = (current - start).days
                    drift_factor = days_since_start / days
                    if drift_factor > 0.7 and max_t:
                        # Slight upward drift in last 30% of period
                        value = round(min(value * (1 + drift_factor * 0.1), normal_max), 4)

                readings_to_create.append(SensorReading(
                    sensor=sensor,
                    value=value,
                    timestamp=current,
                ))

                current += timedelta(minutes=interval_minutes)

        # Bulk create without calling save() (no anomaly detection)
        self.stdout.write(f'Salvando {len(readings_to_create)} leituras no banco...')
        batch_size = 500
        for i in range(0, len(readings_to_create), batch_size):
            batch = readings_to_create[i:i + batch_size]
            SensorReading.objects.bulk_create(batch)
        total_readings = len(readings_to_create)

        # Now run anomaly detection in bulk using Python (not DB save)
        self.stdout.write('Detectando anomalias...')
        readings_with_anomaly = SensorReading.objects.filter(
            sensor__in=sensors
        ).select_related('sensor')

        anomaly_readings = []
        alerts_to_create = []

        for reading in readings_with_anomaly:
            sensor = reading.sensor
            value = float(reading.value)
            min_t = float(sensor.min_threshold) if sensor.min_threshold is not None else None
            max_t = float(sensor.max_threshold) if sensor.max_threshold is not None else None

            if min_t is None and max_t is None:
                continue

            is_out = False
            deviation = 0.0

            if min_t is not None and value < min_t:
                is_out = True
                deviation = abs(value - min_t) / max(abs(min_t), 1) * 100
            if max_t is not None and value > max_t:
                is_out = True
                deviation = abs(value - max_t) / max(abs(max_t), 1) * 100

            if is_out:
                reading.is_anomaly = True
                reading.anomaly_score = round(deviation, 2)
                anomaly_readings.append(reading)

                risk = get_risk_level(round(deviation, 2))
                recommendation = get_recommendation(sensor.sensor_type, risk)
                alerts_to_create.append(Alert(
                    machine=sensor.machine,
                    sensor=sensor,
                    reading=reading,
                    alert_type=Alert.AlertType.THRESHOLD,
                    risk_level=risk,
                    title=f'Anomalia detectada: {sensor.name}',
                    message=(
                        f'Leitura de {value} {sensor.unit} '
                        f'esta fora dos limites (desvio: {round(deviation, 2)}%).'
                    ),
                    recommendation=recommendation,
                ))

        # Update anomaly readings in bulk
        if anomaly_readings:
            SensorReading.objects.bulk_update(anomaly_readings, ['is_anomaly', 'anomaly_score'], batch_size=500)
            total_anomalies = len(anomaly_readings)

        # Create alerts in bulk
        if alerts_to_create:
            Alert.objects.bulk_create(alerts_to_create, batch_size=500)
            total_alerts = len(alerts_to_create)

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed concluido:'
            f'\n  Leituras criadas: {total_readings}'
            f'\n  Anomalias detectadas: {total_anomalies}'
            f'\n  Alertas gerados: {total_alerts}'
        ))
