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
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework.views import APIView

from .forms import AlarmForm
from .models import AlarmSchedule, SirenStatus, ComandoESP

DAYS_MAP = {
		'Mon': 'SEG', 'Tue': 'TER', 'Wed': 'QUA',
		'Thu': 'QUI', 'Fri': 'SEX', 'Sat': 'SAB', 'Sun': 'DOM'
		}


@csrf_exempt
def comando_esp(request):
	if request.method != 'GET':
		return JsonResponse({'error': 'Método não permitido'}, status = 405)
	
	try:
		now = timezone.localtime(timezone.now())
		weekday_en = now.strftime('%a')
		weekday_pt = DAYS_MAP.get(weekday_en, weekday_en)
		current_time = now.time()
		
		# Verifica agendamentos ativos
		agendamentos = AlarmSchedule.objects.filter(
				start_date__lte = now.date(),
				end_date__gte = now.date(),
				days_of_week__contains = weekday_pt,
				active = True
				).order_by('time')
		
		# Verifica se há agendamento no horário atual
		should_activate = False
		for ag in agendamentos:
			if (ag.time.hour == current_time.hour and
					ag.time.minute == current_time.minute):
				should_activate = True
				break
		
		# Verifica comandos manuais pendentes
		manual_command = ComandoESP.objects.filter(comando = 'ligar').first()
		
		response_data = {
				'current_time': now.strftime('%H:%M'),
				'current_day': weekday_pt,
				'should_activate': should_activate or (manual_command is not None),
				'is_scheduled': should_activate and not manual_command,
				'sirene_status': SirenStatus.objects.first().is_on if SirenStatus.objects.exists() else False,
				'next_alarm': None
				}
		
		# Encontra próximo agendamento
		for ag in agendamentos:
			if ag.time > current_time:
				response_data['next_alarm'] = ag.time.strftime('%H:%M')
				break
		
		return JsonResponse(response_data)
	
	except Exception as e:
		return JsonResponse({'error': str(e)}, status = 500)

@csrf_exempt
def ativar_campainha(request):
	if request.method == 'POST':
		try:
			data = json.loads(request.body)
			duration = data.get('duration', 3)  # Default 3 segundos
			
			# Cria/Atualiza o comando
			comando = ComandoESP.objects.update_or_create(
					id = 1,
					defaults = {
							'comando': 'ligar',
							'source': data.get('source', 'manual'),
							'timestamp': timezone.now()
							}
					)
	
			# Atualiza status
			SirenStatus.objects.update_or_create(
					id = 1,
					defaults = {
							'is_on': True,
							'last_activated': timezone.now(),
							'activation_source': data.get('source', 'manual')
							}
					)
			return JsonResponse({
					'status': 'success',
					'command_id': comando[0].id,
					'duration': duration,
					'timestamp': timezone.now().isoformat()
					})
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status = 500)
	return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status = 405)


def check_command(request):
    comando = ComandoESP.objects.first()
    if comando and comando.comando == 'ligar':
        response = {
            'command': 'ligar',
            'source': comando.source,
		    'id': str(comando.id)
        }
        return JsonResponse(response)
    return JsonResponse({'command': 'desligar'})

@csrf_exempt
def confirm_command(request):
    if request.method == 'POST':
        comando = ComandoESP.objects.first()
        if comando:
            comando.comando = 'desligar'
            comando.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def update_alarm(request):
    if request.method == 'POST':
        comando = ComandoESP.objects.first()
        if comando:
            comando.update = 'modoUpdate'  # Atualiza o campo com a hora atual
            comando.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'not found'}, status=404)
    return JsonResponse({'status': 'error'}, status=405)

def isUpdate(request):
    if request.method == 'GET':
        comando = ComandoESP.objects.first()
        if comando:
            return JsonResponse({'update': comando.update})
        else:
            return JsonResponse({'error': 'Nenhum comando encontrado'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@csrf_exempt
def updateConfirm(request):
	if request.method == 'POST':
		comando = ComandoESP.objects.first()
		if comando:
			comando.update = 'modoNormal'
			comando.save()
			return JsonResponse({'status': 'success'})
		else:
			return JsonResponse({'error': 'Nenhum comando encontrado'}, status=404)
	return JsonResponse({'error': 'Método não permitido'}, status=405)

class HomeView(APIView):
	def get(self, request):
		# Converter dia atual para formato do sistema (ex: "DOM")
		weekday_map = {
				'Monday': 'SEG',
				'Tuesday': 'TER',
				'Wednesday': 'QUA',
				'Thursday': 'QUI',
				'Friday': 'SEX',
				'Saturday': 'SAB',
				'Sunday': 'DOM'
				}
		today = timezone.now().strftime('%A')
		today_abbr = weekday_map.get(today, today)
		
		# Query corrigida
		alarms = AlarmSchedule.objects.filter(
				active = True,
				start_date__lte = timezone.now().date(),
				end_date__gte = timezone.now().date(),
				days_of_week__contains = today_abbr
				).order_by('time')
		# Log de agendamentos inativos
		inativos = AlarmSchedule.objects.filter(active = False)
		if inativos.exists():
			print(f"\nAGENDAMENTOS INATIVOS ENCONTRADOS:")
			for alarm in inativos:
				print(f"- ID {alarm.id}: {alarm.time} ({alarm.days_of_week})")
		# DEBUG - Mostrar query no console
		print(f"Agendamentos encontrados: {alarms.count()}")
		for alarm in alarms:
			print(f"- {alarm.event_type} às {alarm.time}")
	
		return render(request, 'index.html', {
				'alarms': alarms,
				'titulo': 'Sistema de Sirene Escolar'
				})

class AlarmListView(ListView):
	"""Lista todos os agendamentos"""
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
			"""Garante ativação mesmo se form enviar active=False"""
			form.instance.active = True
			return super().form_valid(form)

class AlarmUpdateView(UpdateView):
	"""Edita um agendamento existente"""
	model = AlarmSchedule
	form_class = AlarmForm
	template_name = 'alarm_form.html'
	success_url = reverse_lazy('app:alarm-list')
	
	def form_valid(self, form):
		"""Validação adicional do formulário"""
		messages.success(self.request, "Agendamento atualizado com sucesso!")
		form.instance.active = True
		return super().form_valid(form)

class AlarmDeleteView(DeleteView):
	"""Remove um agendamento"""
	model = AlarmSchedule
	template_name = 'alarm_confirm_delete.html'
	success_url = reverse_lazy('app:alarm-list')
	
	def delete(self, request, *args, **kwargs):
		"""Feedback após exclusão"""
		response = super().delete(request, *args, **kwargs)
		messages.success(request, "Agendamento removido com sucesso!")
		return response