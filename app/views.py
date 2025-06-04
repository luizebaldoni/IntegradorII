import json
from django.shortcuts import render, redirect  # adicionamos redirect
from rest_framework.views import APIView
from django.urls import reverse_lazy, reverse  # já tinha reverse_lazy; adicionamos reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib import messages        # para exibir mensagens de sucesso/erro
from django.conf import settings          # para ler ESP_BELL_URL de settings

import requests                            # para fazer o POST ao ESP
from requests.exceptions import RequestException

from .forms import AlarmForm
from .models import Sensor, Device, SensorData, AlarmSchedule, DeviceLog, DeviceConfig

class HomeView(APIView):
	def get(self, request):
		"""
		Renderiza a página inicial e também pode enviar dados se necessário.
		"""
		# Processar os dados para a página inicial
		# Exemplo: passando os dispositivos e sensores para o template
		devices = Device.objects.all()  # Todos os dispositivos
		sensors = Sensor.objects.all()  # Todos os sensores
		alarms = AlarmSchedule.objects.all() # pega todos os agendamentos
  
		# Passar dados para o template
		return render(request, 'index.html', {
            'devices': devices,
            'sensors': sensors,
            'alarms': alarms,
            'title': 'Página Inicial'
        })
                                                 
def post(self, request):
        """
        Espera receber JSON no formato:
        {
          "device_id": "ESP32-1234",
          "device_name": "Campainha-ESP32",
          "sensor_name": "SensTemp",
          "sensor_type": "DHT11",
          "sensor_value": 23.5
        }
        """
        try:
            # Tenta decodificar JSON
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        # 1. Obter ou criar device
        device_id = payload.get('device_id')
        device_name = payload.get('device_name', device_id)
        if not device_id:
            return JsonResponse({'error': 'device_id é obrigatório'}, status=400)

        device, created = Device.objects.get_or_create(
            device_id=device_id,
            defaults={'device_name': device_name}
        )
        if not created:
            # se já existia, atualize o nome (caso tenha mudado)
            if device.device_name != device_name:
                device.device_name = device_name
                device.save()

        # Opcional: registrar no DeviceLog
        DeviceLog.objects.create(
            device=device,
            log_message=f"Dados recebidos do hardware: {payload}"
        )

        # 2. Sensor
        sensor_name = payload.get('sensor_name')
        sensor_type = payload.get('sensor_type')
        sensor_value = payload.get('sensor_value')
        if not sensor_name or sensor_value is None:
            return JsonResponse({'error': 'sensor_name e sensor_value são obrigatórios'}, status=400)

        # Obter ou criar sensor (por nome + tipo)
        sensor, _ = Sensor.objects.get_or_create(
            name=sensor_name,
            sensor_type=sensor_type or '',
            defaults={'value': sensor_value}
        )
        # Criar registro de leitura (SensorData)
        sensor_data_entry = SensorData.objects.create(
            sensor = sensor,
            device = device,
            value  = sensor_value
        )

        # 3. Opcional: associar um DeviceConfig padrão ao device, se não existir
        DeviceConfig.objects.get_or_create(device=device)

        return JsonResponse({
            'message': 'Dados recebidos e processados com sucesso',
            'data': sensor_data_entry.to_dict()
        }, status=201)

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

def ring_bell_now(request):
    """
    View chamada ao clicar em “Tocar Campainha Agora”.
    Faz um POST para o endpoint definido em settings.ESP_BELL_URL.
    Exibe mensagem de sucesso ou erro e volta para a Home.
    """
    esp_url = getattr(settings, 'ESP_BELL_URL', None)
    if not esp_url:
        messages.error(request, "Erro: a URL do ESP (ESP_BELL_URL) não está configurada.")
        return redirect(reverse('app:home'))

    try:
        # Envia um POST vazio para o ESP (ajuste payload se necessário)
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