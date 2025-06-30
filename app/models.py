"""
MODELOS DE BANCO DE DADOS PARA SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo define os modelos utilizados no sistema de sirene escolar, incluindo:
- Cadastro e estado de dispositivos e sensores
- Leitura de dados sensoriais
- Agendamento de eventos automáticos (alarmSchedule)
- Comando remoto para ESP (ComandoESP)
- Controle de status da sirene (SirenStatus)

MODELOS DEFINIDOS:
- Device
- Sensor
- SensorData
- DeviceConfig
- DeviceLog
- GlobalConfig
- ComandoESP
- SirenStatus
- AlarmSchedule
"""

from django.db import models

# ========================================================
# MODELO BASE ABSTRATO COM NOME E DATA DE CRIAÇÃO
# ========================================================

class Model(models.Model):
    """Modelo genérico com campos comuns"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

# ========================================================
# MODELOS RELACIONADOS A DISPOSITIVOS E SENSORES
# ========================================================

class Device(models.Model):
    """Dispositivo IoT (ex: ESP8266, ESP32)"""
    device_id = models.CharField(max_length=100, unique=True)
    device_name = models.CharField(max_length=100)
    last_seen = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default="offline")

    def __str__(self):
        return f"{self.device_name} ({self.device_id})"

class Sensor(models.Model):
    """Sensor associado a um tipo de leitura"""
    name = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=100)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.sensor_type}) - {self.value}"

class SensorData(models.Model):
    """Leitura histórica de sensores"""
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.sensor.name}: {self.value} at {self.timestamp}"

    def to_dict(self):
        """Formata os dados para API"""
        return {
            'sensor_name': self.sensor.name,
            'device_name': self.device.device_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
        }

# ========================================================
# MODELOS DE CONFIGURAÇÃO E LOG
# ========================================================

class DeviceConfig(models.Model):
    """Configurações individuais por dispositivo"""
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    send_interval = models.IntegerField(default=60)
    temp_threshold = models.FloatField(default=30.0)

    def __str__(self):
        return f"Configuração para {self.device.device_name}"

class DeviceLog(models.Model):
    """Logs de eventos dos dispositivos"""
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

# ========================================================
# CONTROLE DE COMANDO E STATUS DA SIRENE
# ========================================================

class ComandoESP(models.Model):
    """Comando enviado do Django para a ESP"""
    comando = models.CharField(max_length=10, default='desligar')
    source = models.CharField(
        max_length=20,
        default='unknown',
        null=True,
        blank=True
    )
    executado = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comando} (Fonte: {self.get_source_display()})"

    def get_source_display(self):
        """Retorna a origem do comando"""
        return self.source if self.source else 'indefinido'

class SirenStatus(models.Model):
    """Indica se a sirene está ligada atualmente"""
    is_on = models.BooleanField(default=False)
    last_activated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Ligada" if self.is_on else "Desligada"

# ========================================================
# AGENDAMENTO DE EVENTOS AUTOMÁTICOS
# ========================================================

class AlarmSchedule(models.Model):
    """Agendamentos para toque automático da sirene"""

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

    active = models.BooleanField(default=True, verbose_name="Ativo")
    event_type = models.CharField(
        max_length=10,
        choices=EventType.choices,
        verbose_name='Tipo de Evento'
    )
    time = models.TimeField(verbose_name='Horário')
    days_of_week = models.CharField(
        max_length=27,  # "SEG,TER,QUA,QUI,SEX,SAB,DOM"
        verbose_name='Dias da Semana'
    )
    start_date = models.DateField(verbose_name='Data de Início')
    end_date = models.DateField(verbose_name='Data de Término')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_event_type_display()} às {self.time.strftime('%H:%M')}"

    def get_days_list(self):
        """Retorna os dias como lista"""
        return [day.strip() for day in self.days_of_week.split(',')]

    def to_json(self):
        """Retorna os dados do agendamento em formato JSON para API"""
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
        """Garante que o agendamento esteja ativo por padrão"""
        if not self.pk or not hasattr(self, 'active'):
            self.active = True
        super().save(*args, **kwargs)
