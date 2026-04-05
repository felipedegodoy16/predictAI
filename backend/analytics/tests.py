import pytest
from django.utils import timezone
from datetime import timedelta
from sensors.models import SensorReading
from alerts.models import Alert


@pytest.mark.django_db
class TestAnalyticsEndpoints:
    def test_dashboard_data(self, admin_client, machine, sensor):
        # Create some readings and alerts for the dashboard to aggregate
        now = timezone.now()
        SensorReading.objects.create(
            sensor=sensor, value=99.0, timestamp=now, is_anomaly=True, anomaly_score=20.0
        )
        Alert.objects.create(
            machine=machine, sensor=sensor, title='Alerta Teste Dashboard',
            alert_type='THRESHOLD', risk_level='HIGH', status='OPEN'
        )

        response = admin_client.get('/api/analytics/dashboard/')
        assert response.status_code == 200
        
        data = response.data
        assert 'machines' in data
        assert data['machines']['total'] == 1
        
        assert 'alerts' in data
        assert data['alerts']['open_total'] == 1
        assert data['alerts']['open_high'] == 1
        
        assert len(data['recent_anomalies']) == 1
        assert len(data['machines_with_most_alerts']) == 1

    def test_machine_patterns(self, admin_client, machine, sensor):
        now = timezone.now()
        SensorReading.objects.create(sensor=sensor, value=20.0, timestamp=now - timedelta(days=1))
        SensorReading.objects.create(sensor=sensor, value=25.0, timestamp=now)
        SensorReading.objects.create(sensor=sensor, value=90.0, timestamp=now + timedelta(days=1), is_anomaly=True)

        response = admin_client.get(f'/api/analytics/machines/{machine.id}/patterns/?days=7')
        assert response.status_code == 200
        
        data = response.data
        assert data['machine_id'] == machine.id
        assert len(data['sensors']) == 1
        
        sensor_data = data['sensors'][0]
        assert sensor_data['sensor_id'] == sensor.id
        assert sensor_data['total_readings'] == 3
        assert sensor_data['anomaly_count'] == 1
        assert sensor_data['avg_value'] == 45.0  # (20+25+90)/3

    def test_failure_prediction(self, admin_client, machine, sensor):
        # Create some sequential readings to establish a trend
        now = timezone.now()
        for i in range(10):
            SensorReading.objects.create(
                sensor=sensor,
                value=20.0 + (i * 2), # Upward trend
                timestamp=now - timedelta(hours=10-i),
                is_anomaly=(i >= 8) # Last 2 are anomalies
            )
            
        response = admin_client.get(f'/api/analytics/machines/{machine.id}/failure-prediction/')
        assert response.status_code == 200
        
        data = response.data
        assert data['machine_id'] == machine.id
        assert len(data['sensors']) == 1
        
        prediction = data['sensors'][0]
        assert 'failure_score' in prediction
        assert 'risk' in prediction
        assert 'trend_slope' in prediction

    def test_maintenance_suggestions(self, admin_client, machine, sensor):
        # Create a trigger for maintenance (open alert)
        Alert.objects.create(
            machine=machine, sensor=sensor, title='Alerta Manutencao',
            alert_type='THRESHOLD', risk_level='HIGH', status='OPEN'
        )
        
        response = admin_client.get('/api/analytics/maintenance-suggestions/')
        assert response.status_code == 200
        
        data = response.data
        assert 'suggestions' in data
        assert len(data['suggestions']) == 1
        assert data['suggestions'][0]['machine_id'] == machine.id
        assert data['suggestions'][0]['priority'] == 'HIGH'
