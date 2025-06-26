import json
import requests
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
from .models import Device, Sensor, AlarmSchedule, DeviceLog, DeviceConfig

# === Endpoint para ESP consultar comando ===
@csrf_exempt
def esp_check(request):
    return HttpResponse("ligar", content_type="text/plain")


@method_decorator(csrf_exempt, name='dispatch')
class HomeView(APIView):
    def get(self, request):
        devices = Device.objects.all()
        sensors = Sensor.objects.all()
        alarms = AlarmSchedule.objects.all()

        return render(request, 'index.html', {
            'devices': devices,
            'sensors': sensors,
            'alarms': alarms,
            'title': 'Página Inicial'
        })

    def post(self, request):
        if request.POST.get('acao') == 'ligar':
            esp_url = getattr(settings, 'ESP_BELL_URL', None)
            if not esp_url:
                messages.error(request, "ESP_BELL_URL não configurado.")
                return redirect('app:home')

            try:
                response = requests.post(esp_url, timeout=5)
                response.raise_for_status()
                messages.success(request, "Campainha acionada com sucesso.")
            except RequestException as e:
                messages.error(request, f"Erro ao acionar campainha: {e}")

        return redirect('app:home')
    
# === ENDPOINT PARA O ESP ===
def comando_esp(request):
    """
    Retorna o comando 'ligar' ou 'desligar' como resposta de texto puro.
    Este endpoint é acessado via HTTP GET pelo ESP8266.
    """
    return HttpResponse("ligar")  # Você pode trocar por "desligar" se quiser testar

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


class AlarmDeleteView(DeleteView):
    model = AlarmSchedule
    template_name = 'alarm_confirm_delete.html'
    success_url = reverse_lazy('app:alarm-list')
