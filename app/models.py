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

class Model(models.Model):
    """Modelo base genérico com campos comuns"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Device(models.Model):
    """Dispositivo IoT conectado ao sistema"""
    device_id = models.CharField(max_length=100, unique=True)
    device_name = models.CharField(max_length=100)
    last_seen = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="offline")

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

class Sensor(models.Model):
    """Sensor físico conectado a um dispositivo"""
    name = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=100)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.sensor_type}) - {self.value}"

class SensorData(models.Model):
    """Registro histórico de leituras de sensores"""
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.sensor.name}: {self.value} at {self.timestamp}"

    def to_dict(self):
        """Converte os dados para formato de dicionário (API)"""
        return {
            'sensor_name': self.sensor.name,
            'device_name': self.device.device_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
        }

class DeviceConfig(models.Model):
    """Configurações específicas para cada dispositivo"""
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    send_interval = models.IntegerField(default=60)
    temp_threshold = models.FloatField(default=30.0)

    def __str__(self):
        return f"Configuração para {self.device.device_name}"

class DeviceLog(models.Model):
    """Registro de logs e eventos dos dispositivos"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    log_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log de {self.device.device_name} em {self.timestamp}"

class GlobalConfig(models.Model):
    """Configurações globais do sistema"""
    api_key = models.CharField(max_length=100)
    data_refresh_interval = models.IntegerField(default=60)

    def __str__(self):
        return "Configuração Global"

class ComandoESP(models.Model):
    """Armazena o último comando enviado para o ESP"""
    comando = models.CharField(max_length=10, default='desligar')
    executado = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comando: {self.comando} (Executado: {self.executado})"

    class Meta:
        verbose_name = "Comando ESP"
        verbose_name_plural = "Comandos ESP"

class SirenStatus(models.Model):
    """Status atual da sirene/campainha"""
    is_on = models.BooleanField(default=False)
    last_activated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Ligada" if self.is_on else "Desligada"

class AlarmSchedule(models.Model):
    """Agendamento de eventos automáticos para a sirene"""
    class EventType(models.TextChoices):
        INICIO_AULA = 'INICIO', 'Início de Aula'
        FIM_AULA = 'FIM', 'Fim de Aula'
        RECREIO = 'RECREIO', 'Recreio'
        TROCA_TURNO = 'TURNO', 'Troca de Turno'
    
    DAYS_CHOICES = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    active = models.BooleanField(
            default = True,  # Garante que o banco de dados crie como ativo
            verbose_name = "Ativo"
            )
    event_type = models.CharField(
        max_length=10,
        choices=EventType.choices,
        verbose_name='Tipo de Evento'
    )
    time = models.TimeField(verbose_name='Horário')
    days_of_week = models.CharField(
        max_length=27,  # Máximo para "SEG,TER,QUA,QUI,SEX,SAB,DOM"
        verbose_name='Dias da Semana'
    )
    start_date = models.DateField(verbose_name='Data de Início')
    end_date = models.DateField(verbose_name='Data de Término')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_event_type_display()} às {self.time.strftime('%H:%M')}"

    def get_days_list(self):
        """Retorna os dias da semana como lista"""
        return [day.strip() for day in self.days_of_week.split(',')]

    def to_json(self):
        """Formata os dados para API"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_display": self.get_event_type_display(),
            "time": self.time.strftime('%H:%M'),
            "days_of_week": self.get_days_list(),
            "start_date": self.start_date.strftime('%Y-%m-%d'),
            "end_date": self.end_date.strftime('%Y-%m-%d'),
            "active": self.active
        }
    
    def save(self, *args, **kwargs):
        """Garante que o agendamento sempre seja ativo ao criar ou atualizar"""
        if not self.pk or not hasattr(self, 'active'):  # Novo registro ou campo não especificado
            self.active = True
        super().save(*args, **kwargs)