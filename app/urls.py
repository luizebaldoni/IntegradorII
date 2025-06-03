from django.urls import path
from .views import HomeView, AlarmListView, AlarmCreateView, AlarmUpdateView, AlarmDeleteView, ring_bell_now

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('agendamentos/', AlarmListView.as_view(), name='alarm-list'),
    path('agendamentos/novo/', AlarmCreateView.as_view(), name='alarm-create'),
    path('agendamentos/editar/<int:pk>/', AlarmUpdateView.as_view(), name='alarm-update'),
    path('agendamentos/remover/<int:pk>/', AlarmDeleteView.as_view(), name='alarm-delete'),
    path('tocar/', ring_bell_now, name='ring-now'),
]