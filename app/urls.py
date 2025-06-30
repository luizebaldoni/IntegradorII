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

# ========================================================
# IMPORTAÇÕES
# ========================================================

from django.urls import path
from .views import (
    HomeView,
    AlarmListView,
    AlarmCreateView,
    AlarmUpdateView,
    AlarmDeleteView,
    comando_esp,
    ativar_campainha,
    check_command,
    confirm_command
)

# ========================================================
# DEFINIÇÃO DAS ROTAS DO APLICATIVO "app"
# ========================================================

urlpatterns = [

    # --------------------------------------------------------
    # ROTAS DE INTERFACE WEB (BASEADAS EM CLASSES)
    # --------------------------------------------------------

    path('', HomeView.as_view(), name='home'),                              # Página inicial com alarmes do dia
    path('agendamentos/', AlarmListView.as_view(), name='alarm-list'),     # Lista de agendamentos
    path('agendamentos/novo/', AlarmCreateView.as_view(), name='alarm-create'),  # Criar novo alarme
    path('agendamentos/editar/<int:pk>/', AlarmUpdateView.as_view(), name='alarm-update'),  # Editar agendamento
    path('agendamentos/remover/<int:pk>/', AlarmDeleteView.as_view(), name='alarm-delete'),  # Excluir agendamento

    # --------------------------------------------------------
    # ENDPOINTS PARA DISPOSITIVOS E COMUNICAÇÃO COM ESP
    # --------------------------------------------------------

    path('api/comando', comando_esp, name='comando-esp'),                   # Endpoint principal para ESP consultar alarmes
    path('ativar/', ativar_campainha, name='ativar-campainha'),            # Ativação manual da sirene
    path('check_command/', check_command, name='check_command'),           # ESP consulta se há comando pendente
    path('confirm_command/', confirm_command, name='confirm_command'),     # ESP confirma execução do comando
]
