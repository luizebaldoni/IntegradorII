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
    list_display = ('event_type', 'time', 'days_of_week', 'active', 'is_active')  # Adicionei 'active' aqui
    list_editable = ('active',)  # Agora está correto pois 'active' está em list_display
    
    @admin.display(boolean = True, description = 'Ativo?')
    def is_active(self, obj):
        return obj.active

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