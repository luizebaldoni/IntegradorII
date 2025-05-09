from django.contrib import admin
from django.urls import path
from app import views
from app.views import *  # Certifique-se de importar a view corretamente

urlpatterns = [
    path('admin/', admin.site.urls),  # Rota para o painel administrativo
    path('', HomeView.as_view(), name='home'),  # Página inicial - Corrigir para associar à HomeView
    path('esp-data/', HomeView.as_view(), name='esp_data'),  # Rota para a comunicação com a ESP
]