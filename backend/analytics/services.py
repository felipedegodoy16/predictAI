from django.db.models import Count, Avg, Min, Max, Q
from django.utils import timezone
from datetime import timedelta


def get_dashboard_data():
    from machines.models import Machine
    from alerts.models import Alert
    from sensors.models import SensorReading

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    machine_summary = {
        'total': Machine.objects.count(),
        'active': Machine.objects.filter(status='ACTIVE').count(),
        'maintenance': Machine.objects.filter(status='MAINTENANCE').count(),
        'inactive': Machine.objects.filter(status='INACTIVE').count(),
    }

    alert_summary = {
        'open_total': Alert.objects.filter(status='OPEN').count(),
        'open_high': Alert.objects.filter(status='OPEN', risk_level='HIGH').count(),
        'open_medium': Alert.objects.filter(status='OPEN', risk_level='MEDIUM').count(),
        'open_low': Alert.objects.filter(status='OPEN', risk_level='LOW').count(),
        'last_24h': Alert.objects.filter(created_at__gte=last_24h).count(),
    }

    recent_anomalies = (
        SensorReading.objects.filter(is_anomaly=True, timestamp__gte=last_24h)
        .select_related('sensor__machine')
        .order_by('-timestamp')[:10]
    )

    machines_with_alerts = (
        Machine.objects.annotate(
            open_alerts=Count('alerts', filter=Q(alerts__status='OPEN'))
        ).filter(open_alerts__gt=0).order_by('-open_alerts')[:5]
    )

    return {
        'machines': machine_summary,
        'alerts': alert_summary,
        'recent_anomalies': recent_anomalies,
        'machines_with_alerts': machines_with_alerts,
    }


def get_machine_patterns(machine_id, days=30):
    from sensors.models import Sensor, SensorReading

    since = timezone.now() - timedelta(days=days)
    sensors = Sensor.objects.filter(machine_id=machine_id, is_active=True)
    patterns = []

    for sensor in sensors:
        readings = SensorReading.objects.filter(sensor=sensor, timestamp__gte=since)
        aggregated = readings.aggregate(
            avg_value=Avg('value'),
            min_value=Min('value'),
            max_value=Max('value'),
            total_readings=Count('id'),
            anomaly_count=Count('id', filter=Q(is_anomaly=True)),
        )
        anomaly_rate = 0
        if aggregated['total_readings']:
            anomaly_rate = round(
                aggregated['anomaly_count'] / aggregated['total_readings'] * 100, 2
            )
        patterns.append({
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'unit': sensor.unit,
            'avg_value': float(aggregated['avg_value']) if aggregated['avg_value'] else None,
            'min_value': float(aggregated['min_value']) if aggregated['min_value'] else None,
            'max_value': float(aggregated['max_value']) if aggregated['max_value'] else None,
            'total_readings': aggregated['total_readings'],
            'anomaly_count': aggregated['anomaly_count'],
            'anomaly_rate_pct': anomaly_rate,
        })

    return patterns


def get_failure_prediction(machine_id, window=50):
    from sensors.models import Sensor, SensorReading
    import numpy as np

    sensors = Sensor.objects.filter(machine_id=machine_id, is_active=True)
    predictions = []

    for sensor in sensors:
        readings = list(
            SensorReading.objects.filter(sensor=sensor)
            .order_by('-timestamp')[:window]
            .values_list('value', 'is_anomaly', 'timestamp')
        )
        if len(readings) < 5:
            continue

        values = [float(r[0]) for r in readings]
        anomaly_flags = [1 if r[1] else 0 for r in readings]

        x = np.arange(len(values))
        if len(x) > 1:
            slope = float(np.polyfit(x, values, 1)[0])
        else:
            slope = 0.0

        recent_anomaly_rate = sum(anomaly_flags[:10]) / min(10, len(anomaly_flags))
        failure_score = min(100, round(recent_anomaly_rate * 60 + abs(slope) * 2, 1))

        if failure_score < 30:
            risk = 'LOW'
            estimated_days = None
        elif failure_score < 60:
            risk = 'MEDIUM'
            estimated_days = 30
        else:
            risk = 'HIGH'
            estimated_days = 7

        predictions.append({
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'failure_score': failure_score,
            'risk': risk,
            'trend_slope': round(slope, 4),
            'estimated_days_to_failure': estimated_days,
            'readings_analyzed': len(readings),
        })

    overall_score = max((p['failure_score'] for p in predictions), default=0)
    return {
        'machine_id': machine_id,
        'overall_failure_score': overall_score,
        'sensors': predictions,
    }


def get_maintenance_suggestions():
    from machines.models import Machine
    from alerts.models import Alert

    thirty_days_ago = timezone.now() - timedelta(days=30)
    machines = Machine.objects.filter(status='ACTIVE')
    suggestions = []

    for machine in machines:
        open_alerts = Alert.objects.filter(
            machine=machine,
            status__in=['OPEN', 'ACKNOWLEDGED'],
            risk_level__in=['MEDIUM', 'HIGH'],
        ).count()

        recent_alerts = Alert.objects.filter(
            machine=machine,
            created_at__gte=thirty_days_ago,
        ).count()

        if open_alerts > 0 or recent_alerts >= 3:
            priority = 'HIGH' if open_alerts > 0 else 'MEDIUM'
            suggestions.append({
                'machine_id': machine.id,
                'machine_name': machine.name,
                'location': machine.location,
                'open_alerts': open_alerts,
                'recent_alerts_30d': recent_alerts,
                'priority': priority,
                'suggestion': (
                    f'Maquina com {open_alerts} alerta(s) aberto(s) e '
                    f'{recent_alerts} ocorrencia(s) nos ultimos 30 dias. '
                    'Agendar manutencao preventiva.'
                ),
            })

    return sorted(suggestions, key=lambda s: s['open_alerts'], reverse=True)
