from django.shortcuts import render  # Importando a função render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Sensor, Device, SensorData  # Importe os modelos necessários


class HomeView(APIView):
	def get(self, request):
		"""
		Renderiza a página inicial e também pode enviar dados se necessário.
		"""
		# Processar os dados para a página inicial
		# Exemplo: passando os dispositivos e sensores para o template
		devices = Device.objects.all()  # Todos os dispositivos
		sensors = Sensor.objects.all()  # Todos os sensores
		
		# Passar dados para o template
		return render(request, 'index.html', {'devices': devices, 'sensors': sensors, 'title': 'Página Inicial'})
	
	def post(self, request):
		"""
		Recebe dados da ESP (por exemplo, sensores) e processa.
		"""
		# Dados da requisição
		sensor_data = request.data  # Os dados da ESP serão passados no corpo da requisição
		
		# Obtendo ou criando o dispositivo
		device, created = Device.objects.get_or_create(device_id = sensor_data.get('device_id'))
		
		# Obtendo o sensor (ou criando um novo, se não existir)
		sensor, created = Sensor.objects.get_or_create(name = sensor_data.get('sensor_name'))
		
		# Salvando a leitura do sensor
		sensor_data_entry = SensorData.objects.create(
				sensor = sensor,
				device = device,
				value = sensor_data.get('sensor_value')
				)
		
		return JsonResponse(
				{'message': 'Dados recebidos e processados com sucesso', 'data': sensor_data_entry.to_dict()})
