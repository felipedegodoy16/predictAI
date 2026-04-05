import pytest
from django.utils import timezone
from sensors.models import SensorReading
from alerts.models import Alert
from datetime import timedelta

@pytest.mark.django_db
class TestSensorEndpoints:
    def test_list_sensors(self, admin_client, sensor):
        response = admin_client.get('/api/sensors/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_create_sensor(self, admin_client, machine):
        data = {
            'machine': machine.id,
            'name': 'Novo Sensor Teste',
            'sensor_type': 'VIBRATION',
            'unit': 'mm/s',
            'min_threshold': 0,
            'max_threshold': 10,
        }
        response = admin_client.post('/api/sensors/', data, format='json')
        assert response.status_code == 201
        assert response.data['name'] == 'Novo Sensor Teste'


@pytest.mark.django_db
class TestSensorReadings:
    def test_create_reading_via_api_key(self, client, machine, sensor):
        url = '/api/sensors/readings/'
        data = {
            'sensor': sensor.id,
            'value': 25.5,
            'timestamp': timezone.now().isoformat()
        }
        response = client.post(url, data, format='json', HTTP_X_API_KEY=str(machine.api_key))
        assert response.status_code == 201
        assert SensorReading.objects.count() == 1

        reading = SensorReading.objects.first()
        # 25.5 is between 10 and 80, so it shouldn't be an anomaly
        assert not reading.is_anomaly
        assert Alert.objects.count() == 0

    def test_create_anomaly_reading_generates_alert(self, client, machine, sensor):
        url = '/api/sensors/readings/'
        data = {
            'sensor': sensor.id,
            'value': 90.0, # Above max_threshold (80)
            'timestamp': timezone.now().isoformat()
        }
        response = client.post(url, data, format='json', HTTP_X_API_KEY=str(machine.api_key))
        assert response.status_code == 201
        
        reading = SensorReading.objects.first()
        assert reading.is_anomaly
        
        # Check generated alert
        assert Alert.objects.count() == 1
        alert = Alert.objects.first()
        assert alert.machine == machine
        assert alert.sensor == sensor
        assert alert.reading == reading
        assert alert.alert_type == 'THRESHOLD'

    def test_invalid_api_key_forbidden(self, client, sensor):
        url = '/api/sensors/readings/'
        data = {
            'sensor': sensor.id,
            'value': 20.0,
            'timestamp': timezone.now().isoformat()
        }
        response = client.post(url, data, format='json', HTTP_X_API_KEY='invalid-uuid-key')
        assert response.status_code == 401

    def test_bulk_create_readings(self, machine, sensor):
        from rest_framework.test import APIClient
        api_client = APIClient()
        url = '/api/sensors/readings/bulk/'
        now = timezone.now()
        data = {
            'readings': [
                {'sensor': sensor.id, 'value': 20.0, 'timestamp': (now - timedelta(minutes=10)).isoformat()},
                {'sensor': sensor.id, 'value': 95.0, 'timestamp': (now - timedelta(minutes=5)).isoformat()}, # Anomaly
                {'sensor': sensor.id, 'value': 25.0, 'timestamp': now.isoformat()},
            ]
        }
        response = api_client.post(url, data, format='json', HTTP_X_API_KEY=str(machine.api_key))
        assert response.status_code == 201
        assert response.data['created'] == 3
        assert response.data['anomalies_detected'] == 1
        assert response.data['alerts_generated'] == 1
        
        assert SensorReading.objects.count() == 3
        assert Alert.objects.count() == 1
        
        # Verify the alert is connected to the right reading
        alert = Alert.objects.first()
        assert alert.reading.value == 95.0
