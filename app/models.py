from django.db import models

"""
MODELOS DE BANCO DE DADOS PARA SISTEMA DE MONITORAMENTO IoT
DESCRIÇÃO:
Este módulo define os modelos de dados utilizados em um sistema de monitoramento baseado em dispositivos IoT,
permitindo o registro de dispositivos, sensores, dados sensoriais, configuração de operação e agendamentos de eventos.

MODELOS:
- Device: representa um dispositivo físico (ex: ESP32)
- Sensor: representa um sensor físico associado a um tipo de dado
- SensorData: registros das leituras dos sensores
- DeviceConfig: configurações específicas por dispositivo
- DeviceLog: log de eventos por dispositivo
- GlobalConfig: configurações gerais do sistema
- AlarmSchedule: agendamento de eventos no calendário semanal
"""

#### MODELO BASE (GENÉRICO) ####
class Model(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

#### DISPOSITIVO IoT ####
class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)      # Identificador único do dispositivo (ex: MAC address)
    device_name = models.CharField(max_length=100)                 # Nome amigável (ex: "ESP32 Sala 1")
    last_seen = models.DateTimeField(auto_now=True)               # Data/hora da última comunicação com o servidor
    status = models.CharField(max_length=20, default="offline")   # Estado atual ("online", "offline", etc.)

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

#### SENSOR FÍSICO ####
class Sensor(models.Model):
    name = models.CharField(max_length=100)                       # Nome do sensor (ex: Temperatura)
    sensor_type = models.CharField(max_length=100)               # Tipo/modelo do sensor (ex: DHT22)
    value = models.FloatField()                                  # Último valor lido
    timestamp = models.DateTimeField(auto_now_add=True)          # Data/hora da última leitura

    def __str__(self):
        return f"{self.name} ({self.sensor_type}) - {self.value}"

#### REGISTRO DE DADOS DE SENSORES ####
class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)  # Referência ao sensor associado
    device = models.ForeignKey(Device, on_delete=models.CASCADE)  # Dispositivo que enviou o dado
    value = models.FloatField()                                   # Valor da leitura
    timestamp = models.DateTimeField(auto_now_add=True)           # Data/hora do registro

    def __str__(self):
        return f"{self.device.device_name} - {self.sensor.name}: {self.value} at {self.timestamp}"

    def to_dict(self):
        # Retorna o dado em formato dicionário para APIs
        return {
            'sensor_name': self.sensor.name,
            'device_name': self.device.device_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
        }

#### CONFIGURAÇÃO INDIVIDUAL DE DISPOSITIVO ####
class DeviceConfig(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE)  # Relacionamento 1:1 com o dispositivo
    send_interval = models.IntegerField(default=60)                  # Intervalo de envio de dados (segundos)
    temp_threshold = models.FloatField(default=30.0)                 # Limite de temperatura para alerta

    def __str__(self):
        return f"Configuração para {self.device.device_name}"

#### LOG DE EVENTOS POR DISPOSITIVO ####
class DeviceLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)  # Dispositivo associado ao log
    log_message = models.TextField()                              # Mensagem registrada (erro, status, etc.)
    timestamp = models.DateTimeField(auto_now_add=True)           # Data/hora do log

    def __str__(self):
        return f"Log de {self.device.device_name} em {self.timestamp}"

#### CONFIGURAÇÕES GLOBAIS DO SISTEMA ####
class GlobalConfig(models.Model):
    api_key = models.CharField(max_length=100)                    # Chave de API para autenticação externa
    data_refresh_interval = models.IntegerField(default=60)       # Intervalo padrão de atualização (segundos)

    def __str__(self):
        return "Configuração Global"

#### AGENDA DE EVENTOS (ESCOLA / AUTOMAÇÃO) ####
class AlarmSchedule(models.Model):

    # Tipos de evento para sinalização
    class EventType(models.TextChoices):
        INICIO_AULA  = 'INICIO',   'Início de Aula'
        FIM_AULA     = 'FIM',      'Fim de Aula'
        RECREIO      = 'RECREIO',  'Recreio'
        TROCA_TURNO  = 'TURNO',    'Troca de Turno'

    # Opções de dias da semana para o campo personalizado no formulário
    DAYS_CHOICES = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]

    time = models.TimeField(verbose_name='Horário')                 # Horário de execução do evento
    event_type = models.CharField(                                  # Tipo de evento programado
        max_length=10,
        choices=EventType.choices,
        verbose_name='Tipo de Evento'
    )

    # Dias da semana para repetição (armazenados como string separada por vírgulas)
    days_of_week = models.CharField(
        max_length=21,
        verbose_name='Dias da Semana',
        help_text='Ex: SEG,TER,QUA para segunda, terça e quarta'
    )

    start_date = models.DateField(verbose_name='Data de Início')    # Data de início da vigência
    end_date = models.DateField(verbose_name='Data de Término')     # Data de fim da vigência

    created_at = models.DateTimeField(auto_now_add=True)            # Registro de criação
    updated_at = models.DateTimeField(auto_now=True)                # Registro de modificação

    def __str__(self):
        # Exemplo: "Início de Aula às 07:30 (2025-03-01 → 2025-12-20)"
        return f"{self.get_event_type_display()} às {self.time.strftime('%H:%M')} ({self.start_date} → {self.end_date})"