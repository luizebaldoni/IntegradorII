from django.contrib import admin
from django.urls import path
from app.views import HomeView  # Certifique-se de importar corretamente a HomeView

urlpatterns = [
    path('admin/', admin.site.urls),  # Rota para o painel administrativo
    path('', HomeView.as_view(), name='home'),  # Página inicial
]
