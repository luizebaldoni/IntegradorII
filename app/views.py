import json
import requests
from requests.exceptions import RequestException

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from rest_framework.views import APIView

from .forms import AlarmForm
from .models import Sensor, Device, SensorData, AlarmSchedule, DeviceLog, DeviceConfig

"""
VIEWS – SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo implementa as views do sistema, incluindo:
- Página inicial com exibição de dispositivos, sensores e alarmes
- Endpoint REST para recebimento de dados dos dispositivos
- CRUD completo para agendamentos de alarme (Create, Read, Update, Delete)
- Execução remota da campainha via POST

CLASSES/VIEW FUNCTIONS:
- HomeView: exibe a página principal e processa requisições de dados (GET/POST)
- AlarmListView: lista os eventos agendados
- AlarmCreateView: cria novo evento
- AlarmUpdateView: edita evento existente
- AlarmDeleteView: exclui um agendamento
- ring_bell_now: dispara a campainha manualmente via ESP
"""

#### VIEW PRINCIPAL (HOME) E RECEBIMENTO DE DADOS VIA API ####
class HomeView(APIView):
    def get(self, request):
        """
        Renderiza a página inicial com a lista de dispositivos,
        sensores e agendamentos configurados no sistema.
        """
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
        """
        Recebe dados dos dispositivos em formato JSON. Esperado:
        {
          "device_id": "ESP32-1234",
          "device_name": "Campainha-ESP32",
          "sensor_name": "SensTemp",
          "sensor_type": "DHT11",
          "sensor_value": 23.5
        }

        Cria ou atualiza registros para:
        - Dispositivo
        - Sensor
        - SensorData
        - DeviceConfig
        - DeviceLog
        """
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        device_id = payload.get('device_id')
        device_name = payload.get('device_name', device_id)

        if not device_id:
            return JsonResponse({'error': 'device_id é obrigatório'}, status=400)

        device, created = Device.objects.get_or_create(
            device_id=device_id,
            defaults={'device_name': device_name}
        )
        if not created and device.device_name != device_name:
            device.device_name = device_name
            device.save()

        # Log da comunicação
        DeviceLog.objects.create(
            device=device,
            log_message=f"Dados recebidos do hardware: {payload}"
        )

        sensor_name = payload.get('sensor_name')
        sensor_type = payload.get('sensor_type')
        sensor_value = payload.get('sensor_value')

        if not sensor_name or sensor_value is None:
            return JsonResponse({'error': 'sensor_name e sensor_value são obrigatórios'}, status=400)

        sensor, _ = Sensor.objects.get_or_create(
            name=sensor_name,
            sensor_type=sensor_type or '',
            defaults={'value': sensor_value}
        )

        # Registro de leitura
        sensor_data_entry = SensorData.objects.create(
            sensor=sensor,
            device=device,
            value=sensor_value
        )

        # Configuração default (caso não exista)
        DeviceConfig.objects.get_or_create(device=device)

        return JsonResponse({
            'message': 'Dados recebidos e processados com sucesso',
            'data': sensor_data_entry.to_dict()
        }, status=201)

#### LISTAGEM DE EVENTOS AGENDADOS ####
class AlarmListView(ListView):
    model = AlarmSchedule
    template_name = 'alarm_list.html'
    context_object_name = 'alarms'

#### CRIAÇÃO DE NOVO EVENTO ####
class AlarmCreateView(CreateView):
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')

#### EDIÇÃO DE EVENTO EXISTENTE ####
class AlarmUpdateView(UpdateView):
    model = AlarmSchedule
    form_class = AlarmForm
    template_name = 'alarm_form.html'
    success_url = reverse_lazy('app:alarm-list')

#### EXCLUSÃO DE EVENTO AGENDADO ####
class AlarmDeleteView(DeleteView):
    model = AlarmSchedule
    template_name = 'alarm_confirm_delete.html'
    success_url = reverse_lazy('app:alarm-list')

#### DISPARO MANUAL DA CAMPAINHA VIA POST ####
def ring_bell_now(request):
    """
    Dispara uma requisição POST para o ESP responsável pelo alarme
    utilizando a URL definida na configuração do sistema (settings.ESP_BELL_URL).

    Exibe mensagem de sucesso ou erro no redirecionamento de volta à página inicial.
    """
    esp_url = getattr(settings, 'ESP_BELL_URL', None)
    if not esp_url:
        messages.error(request, "Erro: a URL do ESP (ESP_BELL_URL) não está configurada.")
        return redirect(reverse('app:home'))

    try:
        response = requests.post(esp_url, timeout=5)
        response.raise_for_status()
    except RequestException as e:
        messages.error(
            request,
            f"Não foi possível tocar a campainha. Erro de conexão com {esp_url}: {e}"
        )
        return redirect(reverse('app:home'))

    messages.success(request, "Campainha tocada com sucesso!")
    return redirect(reverse('app:home'))