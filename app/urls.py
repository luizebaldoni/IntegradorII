"""
ROTAS DO SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Configuração das URLs do sistema, incluindo:
- Rotas para interface web
- Endpoints para API
- URLs administrativas

ROTAS PRINCIPAIS:
- /: Página inicial
- /agendamentos/: Gerenciamento de agendamentos
- /api/comando: Endpoint para dispositivos ESP
- /ativar/: Ativação manual da sirene
"""

from django.urls import path
from .views import (
	HomeView,
	AlarmListView,
	AlarmCreateView,
	AlarmUpdateView,
	AlarmDeleteView,
	comando_esp,
	ativar_campainha, check_command, confirm_command, update_alarm, isUpdate, updateConfirm
	)
app_name = 'app'
urlpatterns = [
		# Páginas web
		path('', HomeView.as_view(), name = 'home'),
		path('agendamentos/', AlarmListView.as_view(), name = 'alarm-list'),
		path('agendamentos/novo/', AlarmCreateView.as_view(), name = 'alarm-create'),
		path('agendamentos/editar/<int:pk>/', AlarmUpdateView.as_view(), name = 'alarm-update'),
		path('agendamentos/remover/<int:pk>/', AlarmDeleteView.as_view(), name = 'alarm-delete'),
		
		# API endpoints
		path('api/comando', comando_esp, name = 'comando-esp'),
		path('ativar/', ativar_campainha, name = 'ativar-campainha'),
		path('check_command/', check_command, name='check_command'),
		path('confirm_command/', confirm_command, name='confirm_command'),
		path('update/', update_alarm, name = 'update'),
		path('isUpdate/', isUpdate, name='isUpdate'),
		path('updateConfirm/', updateConfirm, name = 'updateConfirm'),
		]