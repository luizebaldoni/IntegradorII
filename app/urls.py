from django.urls import path
from .views import *

"""
ROTAS DO APLICATIVO PRINCIPAL – SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo define as rotas específicas do aplicativo principal (`app`), incluindo
a visualização da página inicial, o gerenciamento de agendamentos e a execução imediata
de eventos programados (ex: tocar alarme).

ROTAS DEFINIDAS:
- /                        : página inicial do sistema (dashboard)
- /agendamentos/           : listagem de eventos agendados
- /agendamentos/novo/      : criação de novo evento
- /agendamentos/editar/<id>: edição de evento existente
- /agendamentos/remover/<id>: remoção de evento
- /tocar/                  : execução imediata do toque (alarme manual)
"""
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('agendamentos/', AlarmListView.as_view(), name='alarm-list'),
    path('agendamentos/novo/', AlarmCreateView.as_view(), name='alarm-create'),
    path('agendamentos/editar/<int:pk>/', AlarmUpdateView.as_view(), name='alarm-update'),
    path('agendamentos/remover/<int:pk>/', AlarmDeleteView.as_view(), name='alarm-delete'),
	path('api/comando', comando_esp, name = 'comando-esp'),  # <- esta é a rota para o ESP
]
