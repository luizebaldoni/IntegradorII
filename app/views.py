import json
from time import timezone
from celery import shared_task
import requests
from django.utils.timezone import localtime
from requests.exceptions import RequestException

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import AlarmForm
from .models import *

# === Endpoint para ESP consultar comando ===
@csrf_exempt
def esp_check(request):
    return HttpResponse("ligar", content_type="text/plain")


@method_decorator(csrf_exempt, name = 'dispatch')
class HomeView(APIView):
    def get(self, request):
        dispositivos = Device.objects.all()
        agendamentos = AlarmSchedule.objects.all()
        
        return render(request, 'index.html', {
                'dispositivos': dispositivos,
                'agendamentos': agendamentos,
                'titulo': 'Página Inicial'
                })
    
    def post(self, request):
        acao = request.POST.get('acao')
        
        # Cria uma instância da classe ComandoESP para enviar comandos
        comando_esp = ComandoESP()
        
        if acao == 'ligar':
            try:
                comando_esp.enviar_comando('ligar')
                messages.success(request, "Campainha acionada com sucesso.")
            except Exception as e:
                messages.error(request, f"Erro ao acionar campainha: {e}")
        
        elif acao == 'desligar':
            try:
                comando_esp.enviar_comando('desligar')
                messages.success(request, "Campainha desligada com sucesso.")
            except Exception as e:
                messages.error(request, f"Erro ao desligar campainha: {e}")
        
        return redirect('app:home')

# === ENDPOINT PARA O ESP ===
@csrf_exempt
def comando_esp(request):
    """
    Retorna os agendamentos atuais em formato JSON.
    """
    agendamentos = AlarmSchedule.objects.filter(
            start_date__lte = localtime().date(),
            end_date__gte = localtime().date(),
            days_of_week__contains = localtime().strftime('%a').upper()[:3]
            )
    
    # Serializa os agendamentos
    agendamentos_data = []
    for agendamento in agendamentos:
        agendamentos_data.append({
                'event_type': agendamento.get_event_type_display(),
                'time': agendamento.time.strftime('%H:%M'),
                'days_of_week': agendamento.days_of_week,
                'start_date': agendamento.start_date.isoformat(),
                'end_date': agendamento.end_date.isoformat(),
                })
    
    return JsonResponse({'agendamentos': agendamentos_data})

class AlarmListView(ListView):
    model = AlarmSchedule
    template_name = 'alarm_list.html'
    context_object_name = 'alarms'


class AlarmCreateView(CreateView):
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')


class AlarmUpdateView(UpdateView):
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')

def ativar_campainha(request):
    comando, _ = ComandoESP.objects.get_or_create(id=1)
    comando.comando = 'ligar'
    comando.save()
    return redirect('app:home')

class AlarmDeleteView(DeleteView):
    model = AlarmSchedule
    template_name = 'alarm_confirm_delete.html'
    success_url = reverse_lazy('app:alarm-list')

def verificar_agendamentos():
    # Obter os agendamentos do banco de dados
    agendamentos = AlarmSchedule.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date(),
        days_of_week__contains=timezone.now().strftime('%a').upper()[:3]
    )
    for agendamento in agendamentos:
        if agendamento.time == timezone.now().time():
            ativar_campainha(None)  # Chama a função que ativa a sirene

@shared_task
def verificar_agendamentos_periodicamente():
    verificar_agendamentos()