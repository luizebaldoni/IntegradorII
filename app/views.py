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

DAYS_MAP = {
		'Mon': 'SEG', 'Tue': 'TER', 'Wed': 'QUA',
		'Thu': 'QUI', 'Fri': 'SEX', 'Sat': 'SAB', 'Sun': 'DOM'
		}


@csrf_exempt
def comando_esp(request):
	"""
	Endpoint para o ESP consultar agendamentos ativos

	Retorna:
	- Lista de agendamentos ativos no formato JSON
	- Status atual da sirene
	- Próximo horário agendado
	"""
	if request.method != 'GET':
		return JsonResponse({'error': 'Método não permitido'}, status = 405)
	
	try:
		# Obtém o dia da semana atual no formato PT-BR
		now = timezone.localtime(timezone.now())  # Converte para o fuso horário configurado
		weekday_en = now.strftime('%a')
		weekday_pt = DAYS_MAP.get(weekday_en, weekday_en)
		
		# Filtra agendamentos ativos para o dia atual
		agendamentos = AlarmSchedule.objects.filter(
				start_date__lte = now.date(),
				end_date__gte = now.date(),
				days_of_week__contains = weekday_pt,
				active = True
				).order_by('time')
		
		# Prepara a resposta
		response_data = {
				'current_time': now.strftime('%H:%M'),
				'current_day': weekday_pt,
				'sirene_status': SirenStatus.objects.first().is_on if SirenStatus.objects.exists() else False,
				'agendamentos': [ag.to_json() for ag in agendamentos],
				'proximo_toque': None
				}
		
		# Encontra o próximo agendamento
		current_time = now.time()
		for ag in agendamentos:
			if ag.time > current_time:
				response_data['proximo_toque'] = ag.time.strftime('%H:%M')
				break
		
		return JsonResponse(response_data)
	
	except Exception as e:
		return JsonResponse({'error': str(e)}, status = 500)


@csrf_exempt
def ativar_campainha(request):
	"""
	Ativação manual da sirene/campainha

	Funcionalidades:
	- Ativa a sirene por 1 segundo
	- Registra o comando no banco de dados
	- Atualiza o status da sirene
	"""
	if request.method == 'POST':
		try:
			# Atualiza o status da sirene
			siren, _ = SirenStatus.objects.get_or_create(id = 1)
			siren.is_on = True
			siren.save()
			
			# Cria registro do comando
			ComandoESP.objects.create(comando = 'ligar', executado = False)
			
			messages.success(request, "Campainha acionada com sucesso!")
			return redirect('app:home')
		
		except Exception as e:
			messages.error(request, f"Erro ao acionar campainha: {str(e)}")
			return redirect('app:home')
	return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status = 405)


class HomeView(APIView):
	"""View para a página inicial do sistema"""
	template_name = 'index.html'
	
	def get(self, request):
		context = {
				'alarms': AlarmSchedule.objects.filter(active = True).order_by('time'),
				'siren_status': SirenStatus.objects.first().is_on if SirenStatus.objects.exists() else False,
				'titulo': 'Sistema de Sirene Escolar'
				}
		return render(request, self.template_name, context)


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
		"""Validação adicional do formulário"""
		response = super().form_valid(form)
		messages.success(self.request, "Agendamento criado com sucesso!")
		return response


class AlarmUpdateView(UpdateView):
	"""Edita um agendamento existente"""
	model = AlarmSchedule
	form_class = AlarmForm
	template_name = 'alarm_form.html'
	success_url = reverse_lazy('app:alarm-list')
	
	def form_valid(self, form):
		"""Validação adicional do formulário"""
		response = super().form_valid(form)
		messages.success(self.request, "Agendamento atualizado com sucesso!")
		return response


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