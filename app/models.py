from django.db import models

class Model(models.Model):  # Corrigido para a convenção de nomenclatura
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)  # ID único do dispositivo (pode ser MAC address ou outro identificador)
    device_name = models.CharField(max_length=100)  # Nome do dispositivo (ex: "ESP32-Thermometer")
    last_seen = models.DateTimeField(auto_now=True)  # Data e hora da última comunicação com o servidor
    status = models.CharField(max_length=20, default="offline")  # Status do dispositivo ("online", "offline")

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

class Sensor(models.Model):
    name = models.CharField(max_length=100)  # Nome do sensor (ex: "Temperatura", "Umidade")
    sensor_type = models.CharField(max_length=100)  # Tipo de sensor (ex: "DHT11", "BMP280")
    value = models.FloatField()  # Valor da leitura do sensor
    timestamp = models.DateTimeField(auto_now_add=True)  # Data e hora da leitura

    def __str__(self):
        return f"{self.name} ({self.sensor_type}) - {self.value}"

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.sensor.name}: {self.value} at {self.timestamp}"

    def to_dict(self):
        return {
            'sensor_name': self.sensor.name,
            'device_name': self.device.device_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
        }

class DeviceConfig(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE)  # Relaciona com o modelo Device
    send_interval = models.IntegerField(default=60)  # Intervalo de tempo para envio de dados (em segundos)
    temp_threshold = models.FloatField(default=30.0)  # Limite de temperatura

    def __str__(self):
        return f"Configuração para {self.device.device_name}"


class DeviceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)  # Relaciona com o modelo Device
    log_message = models.TextField()  # Mensagem do log (por exemplo, erro ou status)
    timestamp = models.DateTimeField(auto_now_add=True)  # Data e hora do log

    def __str__(self):
        return f"Log de {self.device.device_name} em {self.timestamp}"

class GlobalConfig(models.Model):
    api_key = models.CharField(max_length=100)  # Chave de API
    data_refresh_interval = models.IntegerField(default=60)  # Intervalo de atualização de dados em segundos

    def __str__(self):
        return "Configuração Global"