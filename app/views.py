"""
VIEWS DO SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Este módulo contém todas as views do sistema, incluindo:
- Views para interface web (CRUD de agendamentos)
- API endpoints para comunicação com dispositivos ESP
- Lógica de controle da sirene/campainha

ENDPOINTS PRINCIPAIS:
- /api/comando: Endpoint para o ESP consultar agendamentos
- /ativar/: Ativação manual da sirene
- /agendamentos/: CRUD de agendamentos
"""

# ========================================================
# IMPORTAÇÕES
# ========================================================

import json
from datetime import datetime, time
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from .forms import AlarmForm
from .models import AlarmSchedule, SirenStatus, ComandoESP

# ========================================================
# MAPEAMENTO DE DIAS DA SEMANA
# ========================================================

DAYS_MAP = {
    'Mon': 'SEG', 'Tue': 'TER', 'Wed': 'QUA',
    'Thu': 'QUI', 'Fri': 'SEX', 'Sat': 'SAB', 'Sun': 'DOM'
}

# ========================================================
# ENDPOINT PRINCIPAL PARA CONSULTA DA ESP
# ========================================================

@csrf_exempt
def comando_esp(request):
    """
    Endpoint que retorna JSON com o comando 'ligar' ou 'desligar' baseado no
    horário atual e na presença de agendamento ou comando manual.

    Retorna:
    - current_time: hora atual formatada
    - current_day: dia da semana
    - should_activate: True se deve ativar a sirene
    - is_scheduled: True se é por agendamento (não manual)
    - sirene_status: status atual da sirene
    - next_alarm: horário do próximo alarme (se houver)
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        now = timezone.localtime(timezone.now())
        weekday_en = now.strftime('%a')
        weekday_pt = DAYS_MAP.get(weekday_en, weekday_en)
        current_time = now.time()

        # Consulta alarmes válidos
        agendamentos = AlarmSchedule.objects.filter(
            start_date__lte=now.date(),
            end_date__gte=now.date(),
            days_of_week__contains=weekday_pt,
            active=True
        ).order_by('time')

        # Verifica se há alarme para o horário atual
        should_activate = any(
            ag.time.hour == current_time.hour and ag.time.minute == current_time.minute
            for ag in agendamentos
        )

        # Verifica comandos manuais pendentes
        manual_command = ComandoESP.objects.filter(comando='ligar').first()

        response_data = {
            'current_time': now.strftime('%H:%M'),
            'current_day': weekday_pt,
            'should_activate': should_activate or (manual_command is not None),
            'is_scheduled': should_activate and not manual_command,
            'sirene_status': SirenStatus.objects.first().is_on if SirenStatus.objects.exists() else False,
            'next_alarm': None
        }

        # Próximo alarme após o horário atual
        for ag in agendamentos:
            if ag.time > current_time:
                response_data['next_alarm'] = ag.time.strftime('%H:%M')
                break

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ========================================================
# ATIVAÇÃO MANUAL DA CAMPANHA
# ========================================================

@csrf_exempt
def ativar_campainha(request):
    """
    Endpoint para ativar a sirene manualmente via POST.
    Cria entrada de comando no banco e atualiza status da sirene.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

    try:
        ComandoESP.objects.all().delete()
        ComandoESP.objects.create(comando='ligar', source='web')

        status = SirenStatus.objects.first() or SirenStatus()
        status.is_on = True
        status.save()

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ========================================================
# VERIFICAÇÃO DO COMANDO PENDENTE PARA A ESP
# ========================================================

@csrf_exempt
def check_command(request):
    """
    Retorna o comando atual ("ligar" ou "desligar") para a ESP.
    """
    comando = ComandoESP.objects.first()

    if not comando or comando.comando != 'ligar':
        return JsonResponse({'command': 'desligar'})

    source = getattr(comando, 'source', 'manual') or 'manual'

    return JsonResponse({
        'command': 'ligar',
        'source': source,
        'id': str(comando.id)
    })

# ========================================================
# CONFIRMAÇÃO DE EXECUÇÃO DO COMANDO PELA ESP
# ========================================================

@csrf_exempt
def confirm_command(request):
    """
    Endpoint chamado pela ESP para confirmar execução do comando.
    Reseta o comando para 'desligar'.
    """
    if request.method == 'POST':
        comando = ComandoESP.objects.first()
        if comando:
            comando.comando = 'desligar'
            comando.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

# ========================================================
# HOME PAGE: VISUALIZAÇÃO DOS AGENDAMENTOS DE HOJE
# ========================================================

class HomeView(APIView):
    """
    Exibe os agendamentos válidos para o dia atual e envia ao template index.html
    """
    def get(self, request):
        weekday_map = {
            'Monday': 'SEG', 'Tuesday': 'TER', 'Wednesday': 'QUA',
            'Thursday': 'QUI', 'Friday': 'SEX', 'Saturday': 'SAB', 'Sunday': 'DOM'
        }
        today = timezone.now().strftime('%A')
        today_abbr = weekday_map.get(today, today)

        alarms = AlarmSchedule.objects.filter(
            active=True,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            days_of_week__contains=today_abbr
        ).order_by('time')

        print(f"Agendamentos encontrados: {alarms.count()}")
        for alarm in alarms:
            print(f"- {alarm.event_type} às {alarm.time}")

        return render(request, 'index.html', {
            'alarms': alarms,
            'titulo': 'Sistema de Sirene Escolar'
        })

# ========================================================
# CRUD DE AGENDAMENTOS
# ========================================================

class AlarmListView(ListView):
    """Lista todos os agendamentos cadastrados"""
    model = AlarmSchedule
    template_name = 'alarm_list.html'
    context_object_name = 'alarms'
    ordering = ['time']


class AlarmCreateView(CreateView):
    """Cria um novo agendamento"""
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')

    def form_valid(self, form):
        """Ativa agendamento por padrão"""
        form.instance.active = True
        return super().form_valid(form)


class AlarmUpdateView(UpdateView):
    """Edita um agendamento existente"""
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')

    def form_valid(self, form):
        """Exibe mensagem de sucesso e força ativação"""
        messages.success(self.request, "Agendamento atualizado com sucesso!")
        form.instance.active = True
        return super().form_valid(form)


class AlarmDeleteView(DeleteView):
    """Remove um agendamento existente"""
    model = AlarmSchedule
    template_name = 'alarm_confirm_delete.html'
    success_url = reverse_lazy('app:alarm-list')

    def delete(self, request, *args, **kwargs):
        """Confirmação com mensagem de feedback"""
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Agendamento removido com sucesso!")
        return response
