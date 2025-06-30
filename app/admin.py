"""
PAINEL ADMINISTRATIVO DJANGO - SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Configuração do painel administrativo do Django para gerenciamento dos dados do sistema de sirene escolar.

MODELOS REGISTRADOS:
- AlarmSchedule: Agendamentos de toques semanais
- SirenStatus: Estado atual da sirene (ligada/desligada)
- ComandoESP: Comandos enviados manualmente ou por agendamento para o ESP
- Device: Dispositivos físicos cadastrados no sistema
- Sensor, SensorData: Monitoramento sensorial de dispositivos
- DeviceConfig, DeviceLog, GlobalConfig: Parâmetros operacionais, logs e configuração global
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

# ========================================================
# CONFIGURAÇÕES DE EXIBIÇÃO PERSONALIZADAS
# ========================================================

class AlarmScheduleAdmin(admin.ModelAdmin):
    """
    Personaliza o formulário de agendamentos:
    - Campo 'active' já vem marcado e bloqueado na criação
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['active'].initial = True
            form.base_fields['active'].disabled = True
        return form

class SirenStatusAdmin(admin.ModelAdmin):
    """
    Configuração de visualização da tabela de status da sirene.
    """
    list_display = ('is_on', 'last_activated')
    readonly_fields = ('last_activated',)

class ComandoESPAdmin(admin.ModelAdmin):
    """
    Configuração da interface de administração dos comandos enviados ao ESP.
    """
    list_display = ('comando', 'executado', 'timestamp')
    readonly_fields = ('timestamp',)
    list_filter = ('executado', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    search_fields = ('comando',)

# ========================================================
# REGISTRO DOS MODELOS NO ADMIN DJANGO
# ========================================================

admin.site.register(AlarmSchedule, AlarmScheduleAdmin)
admin.site.register(SirenStatus, SirenStatusAdmin)
admin.site.register(ComandoESP, ComandoESPAdmin)
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(DeviceConfig)
admin.site.register(DeviceLog)
admin.site.register(GlobalConfig)
