from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from alerts.models import Alert
from machines.models import Machine, MachineStatus
from sensors.models import SensorReading
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
            timestamp__gte=start,
            timestamp__lte=end,
        ).select_related('machine', 'reading')

        if machine_id:
            queryset = queryset.filter(machine_id=machine_id)

        queryset = queryset.order_by('-timestamp')

        if output_format == 'json':
            data = [
                {
                    'id': a.id,
                    'machine': a.machine.serial_number,
                    'type': a.get_alert_type_display(),
                    'criticality': a.get_criticality_display(),
                    'viewed': 'Sim' if a.viewed else 'Nao',
                    'timestamp': a.timestamp.strftime('%d/%m/%Y %H:%M'),
                }
                for a in queryset
            ]
            return Response({'count': len(data), 'results': data})

        headers = ['ID', 'Maquina (Serie)', 'Tipo', 'Criticidade', 'Visualizado', 'Data']
        rows = [
            [
                a.id, a.machine.serial_number,
                a.get_alert_type_display(),
                a.get_criticality_display(),
                'Sim' if a.viewed else 'Nao',
                a.timestamp.strftime('%d/%m/%Y %H:%M'),
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
            total_alerts = Alert.objects.filter(machine=machine, timestamp__gte=start, timestamp__lte=end).count()
            open_alerts = Alert.objects.filter(machine=machine, viewed=False).count()
            high_risk = Alert.objects.filter(machine=machine, criticality=Alert.Criticality.ALTA, timestamp__gte=start, timestamp__lte=end).count()
            total_readings = SensorReading.objects.filter(sensor__machine=machine, timestamp__gte=start, timestamp__lte=end).count()
            
            latest_status = machine.statuses.order_by('-timestamp').first()
            status_display = latest_status.get_status_display() if latest_status else 'Desconhecido'

            rows.append({
                'machine': machine.serial_number,
                'status': status_display,
                'total_alerts': total_alerts,
                'unviewed_alerts': open_alerts,
                'high_risk_alerts': high_risk,
                'total_readings': total_readings,
            })

        if output_format == 'json':
            return Response({'count': len(rows), 'results': rows})

        headers = ['Maquina (Serie)', 'Status', 'Total Alertas', 'Alertas Nao Lidos', 'Alto Risco', 'Leituras']
        export_rows = [
            [r['machine'], r['status'], r['total_alerts'], r['unviewed_alerts'], r['high_risk_alerts'], r['total_readings']]
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
        start, end = _parse_date_range(request)

        queryset = Alert.objects.filter(
            timestamp__gte=start,
            timestamp__lte=end,
        ).select_related('machine', 'reading')

        if risk:
            # try to match risk text to choice
            risk = risk.upper()
            if risk == 'ALTA':
                queryset = queryset.filter(criticality=Alert.Criticality.ALTA)
            elif risk == 'MEDIA':
                queryset = queryset.filter(criticality=Alert.Criticality.MEDIA)
            elif risk == 'BAIXA':
                queryset = queryset.filter(criticality=Alert.Criticality.BAIXA)

        queryset = queryset.order_by('-timestamp')

        headers = ['Maquina', 'Tipo', 'Criticidade', 'Valor Detectado', 'Valor Limite', 'Lido', 'Data']
        rows_data = [
            [
                a.machine.serial_number,
                a.get_alert_type_display(),
                a.get_criticality_display(),
                a.detected_value,
                a.limit_value,
                'Sim' if a.viewed else 'Nao',
                a.timestamp.strftime('%d/%m/%Y %H:%M'),
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

        title = ""
        headers = []
        rows = []
        
        if entity == 'machines':
            title = 'Relatório Geral de Máquinas'
            headers = ['ID', 'Fabricante', 'Numero de Serie', 'Modelo', 'Linha de Producao']
            machines = Machine.objects.all()
            for m in machines:
                rows.append([
                    str(m.id),
                    m.manufacturer,
                    m.serial_number,
                    m.model or '-',
                    m.production_line or '-'
                ])
                
        elif entity == 'users':
            title = 'Relatório Dinâmico de Usuários'
            headers = ['Nome', 'Email', 'Perfil', 'Status do Acesso', 'Ultimo Login']
            users = User.objects.all()
            for u in users:
                rows.append([
                    u.name,
                    u.email,
                    u.get_profile_display(),
                    'Ativo' if u.is_active else 'Desativado',
                    u.last_login.strftime('%d/%m/%Y %H:%M') if u.last_login else 'Nunca'
                ])
                
        elif entity == 'audit':
            title = 'Relatório de Logs de Auditoria'
            headers = ['Data/Hora', 'Usuário', 'Tabela', 'ID Registro', 'Campo', 'Valor Antigo', 'Valor Novo']
            logs = AuditLog.objects.all().select_related('user')[:500]
            for log in logs:
                rows.append([
                    log.timestamp.strftime('%d/%m/%Y %H:%M'),
                    log.user.name if log.user else 'Sistema',
                    log.table_name,
                    str(log.record_id),
                    log.field_name,
                    log.old_value,
                    log.new_value
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
