"""
PAINEL ADMINISTRATIVO DJANGO - SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Configuração do painel administrativo do Django para gerenciamento dos dados do sistema.

MODELOS REGISTRADOS:
- AlarmSchedule: Agendamentos de toques
- SirenStatus: Status atual da sirene
- ComandoESP: Comandos enviados para os dispositivos
- Device: Dispositivos IoT cadastrados
"""

from django.contrib import admin
from .models import (
    AlarmSchedule, 
    SirenStatus, 
    ComandoESP,
    Device,
    Sensor,
    SensorData,
    DeviceConfig,
    DeviceLog,
    GlobalConfig
)


class AlarmScheduleAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Somente durante a CRIAÇÃO
            form.base_fields['active'].initial = True
            form.base_fields['active'].disabled = True  # Opcional: bloqueia alteração
        return form
class SirenStatusAdmin(admin.ModelAdmin):
    """Configuração do admin para status da sirene"""
    list_display = ('is_on', 'last_activated')
    readonly_fields = ('last_activated',)

class ComandoESPAdmin(admin.ModelAdmin):
    """Configuração do admin para comandos"""
    list_display = ('comando', 'executado', 'timestamp')
    readonly_fields = ('timestamp',)
    list_filter = ('executado', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    search_fields = ('comando',)
    
# Registro dos modelos
admin.site.register(AlarmSchedule, AlarmScheduleAdmin)
admin.site.register(SirenStatus, SirenStatusAdmin)
admin.site.register(ComandoESP, ComandoESPAdmin)
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(DeviceConfig)
admin.site.register(DeviceLog)
admin.site.register(GlobalConfig)