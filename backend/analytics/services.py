from django.db.models import Count, Avg, Min, Max, Q, F
from django.utils import timezone
from datetime import timedelta


def get_dashboard_data():
    from machines.models import Machine, MachineStatus
    from alerts.models import Alert
    from sensors.models import SensorReading

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    # Simplified status logic: since status is now an event history, 
    # counting current status correctly requires a subquery or aggregation.
    # For MVP, just return total machines.
    machine_summary = {
        'total': Machine.objects.count(),
        'active': 0,
        'maintenance': 0,
        'inactive': 0,
    }

    alert_summary = {
        'open_total': Alert.objects.filter(viewed=False).count(),
        'open_high': Alert.objects.filter(viewed=False, criticality=Alert.Criticality.ALTA).count(),
        'open_medium': Alert.objects.filter(viewed=False, criticality=Alert.Criticality.MEDIA).count(),
        'open_low': Alert.objects.filter(viewed=False, criticality=Alert.Criticality.BAIXA).count(),
        'last_24h': Alert.objects.filter(timestamp__gte=last_24h).count(),
    }

    recent_anomalies = (
        SensorReading.objects.filter(value__gt=F('sensor__limit_temp'), sensor__limit_temp__isnull=False, timestamp__gte=last_24h)
        .select_related('machine')
        .order_by('-timestamp')[:10]
    )

    machines_with_alerts = (
        Machine.objects.annotate(
            open_alerts=Count('alerts', filter=Q(alerts__viewed=False))
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
        )
        # Anomaly logic based on limit_temp
        anomaly_count = 0
        if sensor.limit_temp:
            anomaly_count = readings.filter(value__gt=sensor.limit_temp).count()

        anomaly_rate = 0
        if aggregated['total_readings']:
            anomaly_rate = round(
                anomaly_count / aggregated['total_readings'] * 100, 2
            )
        patterns.append({
            'sensor_id': sensor.id,
            'sensor_name': sensor.sensor_type,
            'sensor_type': sensor.sensor_type,
            'unit': sensor.unit,
            'avg_value': float(aggregated['avg_value']) if aggregated['avg_value'] else None,
            'min_value': float(aggregated['min_value']) if aggregated['min_value'] else None,
            'max_value': float(aggregated['max_value']) if aggregated['max_value'] else None,
            'total_readings': aggregated['total_readings'],
            'anomaly_count': anomaly_count,
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
            .values_list('value', 'timestamp')
        )
        if len(readings) < 5:
            continue

        values = [float(r[0]) for r in readings]
        limit = sensor.limit_temp or max(values) * 1.5
        
        anomaly_flags = [1 if v > limit else 0 for v in values]

        x = np.arange(len(values))
        if len(x) > 1:
            slope = float(np.polyfit(x, values, 1)[0])
        else:
            slope = 0.0

        recent_anomaly_rate = sum(anomaly_flags[:10]) / min(10, len(anomaly_flags))
        failure_score = min(100, round(recent_anomaly_rate * 60 + abs(slope) * 2, 1))

        if failure_score < 30:
            risk = 'BAIXA'
            estimated_days = None
        elif failure_score < 60:
            risk = 'MEDIA'
            estimated_days = 30
        else:
            risk = 'ALTA'
            estimated_days = 7

        predictions.append({
            'sensor_id': sensor.id,
            'sensor_name': sensor.sensor_type,
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
    machines = Machine.objects.all()
    suggestions = []

    for machine in machines:
        open_alerts = Alert.objects.filter(
            machine=machine,
            viewed=False,
            criticality__in=[Alert.Criticality.MEDIA, Alert.Criticality.ALTA],
        ).count()

        recent_alerts = Alert.objects.filter(
            machine=machine,
            timestamp__gte=thirty_days_ago,
        ).count()

        if open_alerts > 0 or recent_alerts >= 3:
            priority = 'ALTA' if open_alerts > 0 else 'MEDIA'
            suggestions.append({
                'machine_id': machine.id,
                'machine_serial': machine.serial_number,
                'open_alerts': open_alerts,
                'recent_alerts_30d': recent_alerts,
                'priority': priority,
                'suggestion': (
                    f'Maquina com {open_alerts} alerta(s) nao lido(s) e '
                    f'{recent_alerts} ocorrencia(s) nos ultimos 30 dias. '
                    'Agendar manutencao preventiva.'
                ),
            })

    return sorted(suggestions, key=lambda s: s['open_alerts'], reverse=True)
