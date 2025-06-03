from django.contrib import admin
from .models import Sensor, SensorData, Device, DeviceLog, DeviceConfig, GlobalConfig, AlarmSchedule

# Registrando os modelos no painel administrativo
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(Device)
admin.site.register(DeviceLog)
admin.site.register(DeviceConfig)
admin.site.register(GlobalConfig)
admin.site.register(AlarmSchedule)