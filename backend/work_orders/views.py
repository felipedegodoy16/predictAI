from django.db import models as django_models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WorkOrder, Maintenance, WorkOrderStatus
from .serializers import WorkOrderSerializer, MaintenanceSerializer, WorkOrderStatusSerializer
from users.permissions import IsTechOpTaskPermission, IsAdminOrManager


class WorkOrderStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista as colunas do Kanban. Read-only — os status são gerenciados pelo admin."""
    queryset = WorkOrderStatus.objects.all()
    serializer_class = WorkOrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkOrderViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsTechOpTaskPermission]
    filterset_fields = ['status', 'priority', 'order_type', 'machine', 'assigned_to']
    search_fields = ['machine__serial_number', 'production_line']
    ordering_fields = ['opening_date', 'status', 'priority']
    ordering = ['-opening_date']

    def get_queryset(self):
        user = self.request.user
        base_qs = WorkOrder.objects.select_related(
            'machine', 'opened_by', 'assigned_to', 'status'
        ).all()

        days_param = self.request.query_params.get('days')
        if days_param is not None:
            try:
                days = int(days_param)
                from django.utils import timezone
                from datetime import timedelta
                limit_date = timezone.now() - timedelta(days=days)
                base_qs = base_qs.filter(opening_date__gte=limit_date)
            except ValueError:
                pass

        return base_qs

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def move_status(self, request, pk=None):
        """Endpoint dedicado para mover OS entre colunas do Kanban.
        Qualquer usuário autenticado pode usar — não requer ser admin ou criador."""
        try:
            wo = WorkOrder.objects.select_related(
                'machine', 'opened_by', 'assigned_to', 'status'
            ).get(pk=pk)
        except WorkOrder.DoesNotExist:
            return Response({'error': 'OS não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        new_status_id = request.data.get('status')
        if not new_status_id:
            return Response({'error': 'Campo status é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_status = WorkOrderStatus.objects.get(pk=new_status_id)
        except WorkOrderStatus.DoesNotExist:
            return Response({'error': 'Status inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        wo.status = new_status
        wo.save(update_fields=['status'])
        serializer = WorkOrderSerializer(wo, context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        wo = serializer.save(opened_by=self.request.user)

        # Create a notification for the user who created it
        from notifications.models import Notification
        from django.contrib.auth import get_user_model

        Notification.objects.create(
            user=self.request.user,
            title=f"Nova OS Criada: OS-{wo.id}",
            message=f"Você abriu uma nova OS do tipo {wo.order_type} para a máquina {wo.machine.serial_number if wo.machine else 'Desconhecida'}.",
            notification_type=Notification.NotificationType.INFO
        )

        # Notificar o técnico atribuído (se diferente do criador)
        if wo.assigned_to and wo.assigned_to != self.request.user:
            Notification.objects.create(
                user=wo.assigned_to,
                title=f"OS Atribuída a Você: OS-{wo.id}",
                message=f"Uma OS do tipo {wo.order_type} foi atribuída a você pelo usuário {self.request.user.name}.",
                notification_type=Notification.NotificationType.WARNING
            )

        # Integrar com GROQ API
        import os
        api_key = os.environ.get('GROQ_API_KEY', '')
        if api_key and getattr(wo, 'machine', None):
            machine = wo.machine
            prompt = (
                f"Crie uma descrição técnica, profissional e 'bem legal' para uma Ordem de Serviço "
                f"do tipo '{wo.order_type}'. A máquina envolvida é {machine.manufacturer} {machine.model} "
                f"(S/N: {machine.serial_number}). "
            )
            if wo.observation:
                prompt += f"O usuário reportou o seguinte problema inicial: '{wo.observation}'. "
            prompt += "Gere apenas o texto da descrição a ser colocado na OS, sem aspas, focado na resolução e na clareza."

            import urllib.request
            import json
            try:
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    data=json.dumps({
                        "model": "llama3-8b-8192",
                        "messages": [
                            {"role": "system", "content": "Você é um assistente técnico especialista em manutenção industrial preditiva e corretiva."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 512
                    }).encode('utf-8')
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    ai_text = data["choices"][0]["message"]["content"].strip()
                    if wo.observation:
                        wo.observation = f"{wo.observation}\n\n--- Análise IA (Groq) ---\n{ai_text}"
                    else:
                        wo.observation = ai_text
                    wo.save(update_fields=['observation'])
            except Exception as e:
                print("Error calling Groq API:", e)

        # Also notify admins if the creator is not an admin
        if self.request.user.profile != 'administrador':
            User = get_user_model()
            admins = User.objects.filter(profile='administrador')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title=f"Nova OS Reportada: OS-{wo.id}",
                    message=f"O usuário {self.request.user.email} abriu uma nova OS do tipo {wo.order_type}.",
                    notification_type=Notification.NotificationType.WARNING
                )


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_fields = ['machine', 'work_order']
    search_fields = ['description', 'solution']
    ordering_fields = ['performed_date']
    ordering = ['-performed_date']
