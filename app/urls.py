from django.urls import path
from .views import HomeView, AlarmListView, AlarmCreateView, AlarmUpdateView, AlarmDeleteView, ring_bell_now

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

app_name = 'app'  # Namespace para uso com {% url 'app:alarm-list' %}, etc.

urlpatterns = [
    path('', HomeView.as_view(), name='home'),                                # Página inicial (dashboard)
    path('agendamentos/', AlarmListView.as_view(), name='alarm-list'),        # Listagem dos eventos agendados
    path('agendamentos/novo/', AlarmCreateView.as_view(), name='alarm-create'), # Criação de novo agendamento
    path('agendamentos/editar/<int:pk>/', AlarmUpdateView.as_view(), name='alarm-update'), # Edição de agendamento
    path('agendamentos/remover/<int:pk>/', AlarmDeleteView.as_view(), name='alarm-delete'), # Exclusão de agendamento
    path('tocar/', ring_bell_now, name='ring-now'),                           # Disparo manual do alarme
]
