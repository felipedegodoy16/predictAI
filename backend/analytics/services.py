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

def get_chart_data(days=14):
    from sensors.models import SensorReading
    from alerts.models import Alert
    from machines.models import Machine
    from django.db.models.functions import TruncDate
    
    start_date = timezone.now() - timedelta(days=days)

    # 1. Encontrar as 2 máquinas com mais alertas
    top_machines = list(
        Machine.objects.annotate(alert_count=Count('alerts'))
        .order_by('-alert_count')[:2]
    )

    machine1_name = "Máquina 1"
    machine2_name = "Máquina 2"
    series1_data = []
    series2_data = []
    sorted_dates = []

    if top_machines:
        m1 = top_machines[0]
        machine1_name = f"{m1.manufacturer} {m1.model}"
        m2 = top_machines[1] if len(top_machines) > 1 else None
        if m2:
            machine2_name = f"{m2.manufacturer} {m2.model}"
        
        def get_daily_avg_for_machine(machine_obj):
            readings = (
                SensorReading.objects.filter(machine=machine_obj, sensor__sensor_type__icontains='Temp', timestamp__gte=start_date)
                .annotate(date=TruncDate('timestamp'))
                .values('date')
                .annotate(avg_val=Avg('value'))
                .order_by('date')
            )
            return {r['date'].strftime('%Y-%m-%d'): round(float(r['avg_val']), 2) for r in readings}

        m1_data = get_daily_avg_for_machine(m1)
        m2_data = get_daily_avg_for_machine(m2) if m2 else {}

        dates_set = set(m1_data.keys()).union(set(m2_data.keys()))
        sorted_dates = sorted(list(dates_set))

        series1_data = [m1_data.get(d, 0) for d in sorted_dates]
        series2_data = [m2_data.get(d, 0) for d in sorted_dates]

    # Agrupamento de Alertas por Máquina para o gráfico de barras
    alerts_agg = (
        Alert.objects.filter(timestamp__gte=start_date)
        .values(machine_name=F('machine__manufacturer'))
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    alerts_machines = []
    alerts_counts = []
    for a in alerts_agg:
        alerts_machines.append(a['machine_name'])
        alerts_counts.append(a['total'])

    return {
        "dates": sorted_dates,
        "legend_1": machine1_name,
        "legend_2": machine2_name,
        "series_1_data": series1_data,
        "series_2_data": series2_data,
        
        # Mantendo para compatibilidade caso outro gráfico use
        "temp_series": series1_data,
        "vib_series": series2_data,

        "alerts_machines": alerts_machines,
        "alerts_counts": alerts_counts
    }
