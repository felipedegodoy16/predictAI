from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from sensors.serializers import SensorReadingSerializer
from machines.serializers import MachineListSerializer
from .services import (
    get_dashboard_data,
    get_machine_patterns,
    get_failure_prediction,
    get_maintenance_suggestions,
)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_dashboard_data()
        return Response({
            'machines': data['machines'],
            'alerts': data['alerts'],
            'recent_anomalies': SensorReadingSerializer(data['recent_anomalies'], many=True).data,
            'machines_with_most_alerts': MachineListSerializer(data['machines_with_alerts'], many=True).data,
        }, status=status.HTTP_200_OK)


class MachinePatternsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, machine_id):
        days = int(request.query_params.get('days', 30))
        patterns = get_machine_patterns(machine_id, days=days)
        return Response({
            'machine_id': machine_id,
            'period_days': days,
            'sensors': patterns,
        }, status=status.HTTP_200_OK)


class FailurePredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, machine_id):
        window = int(request.query_params.get('window', 50))
        prediction = get_failure_prediction(machine_id, window=window)
        return Response(prediction, status=status.HTTP_200_OK)


class MaintenanceSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suggestions = get_maintenance_suggestions()
        return Response({'suggestions': suggestions}, status=status.HTTP_200_OK)
