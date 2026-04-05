from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from alerts.models import Alert
from machines.models import Machine
from sensors.models import SensorReading
from suppliers.models import Supplier
from users.models import User
from audit.models import AuditLog
from .generators import generate_pdf, generate_excel
import csv


def _parse_date_range(request):
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if not start:
        start = (timezone.now() - timedelta(days=30)).isoformat()
    if not end:
        end = timezone.now().isoformat()
    return start, end


class FailureReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        output_format = request.query_params.get('output', 'json')
        machine_id = request.query_params.get('machine')
        start, end = _parse_date_range(request)

        queryset = Alert.objects.filter(
            created_at__gte=start,
            created_at__lte=end,
        ).select_related('machine', 'sensor', 'resolved_by')

        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        queryset = queryset.order_by('-created_at')

        if output_format == 'json':
            data = [
                {
                    'id': a.id,
                    'machine': a.machine.name,
                    'sensor': a.sensor.name if a.sensor else '-',
                    'title': a.title,
                    'risk_level': a.get_risk_level_display(),
                    'status': a.get_status_display(),
                    'created_at': a.created_at.strftime('%d/%m/%Y %H:%M'),
                    'resolved_at': a.resolved_at.strftime('%d/%m/%Y %H:%M') if a.resolved_at else '-',
                }
                for a in queryset
            ]
            return Response({'count': len(data), 'results': data})

        headers = ['ID', 'Maquina', 'Sensor', 'Titulo', 'Risco', 'Status', 'Criado em', 'Resolvido em']
        rows = [
            [
                a.id, a.machine.name,
                a.sensor.name if a.sensor else '-',
                a.title,
                a.get_risk_level_display(),
                a.get_status_display(),
                a.created_at.strftime('%d/%m/%Y %H:%M'),
                a.resolved_at.strftime('%d/%m/%Y %H:%M') if a.resolved_at else '-',
            ]
            for a in queryset
        ]
        summary = {'Periodo': f'{start[:10]} a {end[:10]}', 'Total de registros': len(rows)}

        if output_format == 'pdf':
            buffer = generate_pdf('Relatorio de Falhas', headers, rows, summary)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_falhas.pdf"'
            return response

        if output_format == 'xlsx':
            buffer = generate_excel('Relatorio de Falhas', headers, rows, sheet_name='Falhas')
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="relatorio_falhas.xlsx"'
            return response

        return Response({'detail': 'Formato invalido. Use: json, pdf ou xlsx.'}, status=400)


class PerformanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        output_format = request.query_params.get('output', 'json')
        machine_id = request.query_params.get('machine')
        start, end = _parse_date_range(request)

        machines = Machine.objects.all()
        if machine_id:
            machines = machines.filter(id=machine_id)

        rows = []
        for machine in machines:
            total_alerts = Alert.objects.filter(machine=machine, created_at__gte=start, created_at__lte=end).count()
            open_alerts = Alert.objects.filter(machine=machine, status='OPEN').count()
            high_risk = Alert.objects.filter(machine=machine, risk_level='HIGH', created_at__gte=start, created_at__lte=end).count()
            total_readings = SensorReading.objects.filter(sensor__machine=machine, timestamp__gte=start, timestamp__lte=end).count()
            anomalies = SensorReading.objects.filter(sensor__machine=machine, is_anomaly=True, timestamp__gte=start, timestamp__lte=end).count()
            anomaly_rate = round(anomalies / total_readings * 100, 2) if total_readings else 0

            rows.append({
                'machine': machine.name,
                'status': machine.get_status_display(),
                'location': machine.location,
                'total_alerts': total_alerts,
                'open_alerts': open_alerts,
                'high_risk_alerts': high_risk,
                'total_readings': total_readings,
                'anomaly_rate_pct': anomaly_rate,
            })

        if output_format == 'json':
            return Response({'count': len(rows), 'results': rows})

        headers = ['Maquina', 'Status', 'Localizacao', 'Total Alertas', 'Alertas Abertos', 'Alto Risco', 'Leituras', 'Taxa Anomalia (%)']
        export_rows = [
            [r['machine'], r['status'], r['location'], r['total_alerts'], r['open_alerts'], r['high_risk_alerts'], r['total_readings'], r['anomaly_rate_pct']]
            for r in rows
        ]
        summary = {'Periodo': f'{start[:10]} a {end[:10]}', 'Maquinas analisadas': len(rows)}

        if output_format == 'pdf':
            buffer = generate_pdf('Relatorio de Desempenho', headers, export_rows, summary)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_desempenho.pdf"'
            return response

        if output_format == 'xlsx':
            buffer = generate_excel('Relatorio de Desempenho', headers, export_rows, sheet_name='Desempenho')
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="relatorio_desempenho.xlsx"'
            return response

        return Response({'detail': 'Formato invalido. Use: json, pdf ou xlsx.'}, status=400)


class AlertReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        output_format = request.query_params.get('output', 'json')
        risk = request.query_params.get('risk')
        status_filter = request.query_params.get('status')
        start, end = _parse_date_range(request)

        queryset = Alert.objects.filter(
            created_at__gte=start,
            created_at__lte=end,
        ).select_related('machine', 'sensor')

        if risk:
            queryset = queryset.filter(risk_level=risk.upper())
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        queryset = queryset.order_by('-created_at')

        headers = ['Maquina', 'Sensor', 'Tipo', 'Risco', 'Status', 'Titulo', 'Recomendacao', 'Data']
        rows_data = [
            [
                a.machine.name,
                a.sensor.name if a.sensor else '-',
                a.get_alert_type_display(),
                a.get_risk_level_display(),
                a.get_status_display(),
                a.title,
                a.recommendation[:80] if a.recommendation else '-',
                a.created_at.strftime('%d/%m/%Y %H:%M'),
            ]
            for a in queryset
        ]

        if output_format == 'json':
            return Response({'count': len(rows_data), 'results': rows_data})

        summary = {'Periodo': f'{start[:10]} a {end[:10]}', 'Total': len(rows_data)}

        if output_format == 'pdf':
            buffer = generate_pdf('Relatorio de Alertas', headers, rows_data, summary)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_alertas.pdf"'
            return response

        if output_format == 'xlsx':
            buffer = generate_excel('Relatorio de Alertas', headers, rows_data, sheet_name='Alertas')
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="relatorio_alertas.xlsx"'
            return response

        return Response({'detail': 'Formato invalido. Use: json, pdf ou xlsx.'}, status=400)


class DynamicExportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        entity = request.data.get('entity')
        output_format = request.data.get('output', 'csv')
        
        if not entity:
            return Response({'detail': 'Entidade (entity) e obrigatoria.'}, status=400)

        # Basic entity resolution directly pulling all data for MVP
        title = ""
        headers = []
        rows = []
        
        if entity == 'machines':
            title = 'Relatório Geral de Máquinas'
            headers = ['ID', 'Nome', 'Numero de Serie', 'Fornecedor', 'Modelo', 'Localizacao', 'Status']
            machines = Machine.objects.all().select_related('supplier')
            for m in machines:
                rows.append([
                    str(m.id),
                    m.name,
                    m.serial_number,
                    m.supplier.name if m.supplier else '-',
                    m.model or '-',
                    m.location or '-',
                    m.get_status_display()
                ])
                
        elif entity == 'suppliers':
            title = 'Relatório de Fornecedores Ativos'
            headers = ['ID', 'Fornecedor', 'CNPJ', 'Email de Contato', 'Telefone', 'Status']
            suppliers = Supplier.objects.all()
            for s in suppliers:
                rows.append([
                    str(s.id),
                    s.name,
                    s.cnpj,
                    s.email,
                    s.phone or '-',
                    'Ativo' if s.is_active else 'Inativo'
                ])
                
        elif entity == 'users':
            title = 'Relatório Dinâmico de Usuários'
            headers = ['Nome', 'Email', 'Cargo', 'Status do Acesso', 'Ultimo Login']
            users = User.objects.all()
            for u in users:
                rows.append([
                    u.name,
                    u.email,
                    u.get_role_display(),
                    'Ativo' if u.is_active else 'Desativado',
                    u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else 'Nunca'
                ])
                
        elif entity == 'audit':
            title = 'Relatório de Logs de Auditoria'
            headers = ['Data/Hora', 'Usuário', 'Ação', 'Alvo', 'Descrição']
            logs = AuditLog.objects.all().select_related('user')[:500] # Limite para não sobrecarregar
            for log in logs:
                rows.append([
                    log.timestamp.strftime('%d/%m/%Y %H:%M'),
                    log.user.name if log.user else 'Sistema',
                    log.get_action_display(),
                    log.entity_type,
                    log.description
                ])
        else:
            return Response({'detail': 'Entidade desconhecida.'}, status=400)

        summary = {'Total de Registros': len(rows), 'Entidade Fonte': entity.upper()}

        if output_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="export_{entity}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([title])
            writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
            return response

        elif output_format == 'pdf':
            buffer = generate_pdf(title, headers, rows, summary)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="export_{entity}.pdf"'
            return response

        elif output_format == 'xlsx':
            buffer = generate_excel(title, headers, rows, sheet_name='Exportacao')
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="export_{entity}.xlsx"'
            return response

        return Response({'detail': 'Formato invalido. Suportados: csv, xlsx, pdf.'}, status=400)
