from django.contrib import admin
from .models import Sensor, SensorData, Device, DeviceLog, DeviceConfig, GlobalConfig

# Registrando os modelos no painel administrativo
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(Device)
admin.site.register(DeviceLog)
admin.site.register(DeviceConfig)
admin.site.register(GlobalConfig)
