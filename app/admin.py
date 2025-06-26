from django.contrib import admin
from .models import Sensor, SensorData, Device, DeviceLog, DeviceConfig, GlobalConfig, AlarmSchedule

"""
REGISTRO DE MODELOS NO ADMINISTRADOR DJANGO – SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo registra todos os modelos de dados no painel administrativo do Django,
permitindo a visualização, edição e gerenciamento via interface web.

MODELOS REGISTRADOS:
- Sensor: sensores físicos utilizados no sistema
- SensorData: registros de medições coletadas
- Device: dispositivos IoT (ex: ESP32)
- DeviceLog: eventos e mensagens de log dos dispositivos
- DeviceConfig: configurações individuais por dispositivo
- GlobalConfig: parâmetros globais do sistema
- AlarmSchedule: agendamento de eventos automáticos
"""

# Registro dos modelos no painel administrativo Django
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(Device)
admin.site.register(DeviceLog)
admin.site.register(DeviceConfig)
admin.site.register(GlobalConfig)
admin.site.register(AlarmSchedule)
