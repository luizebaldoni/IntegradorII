from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Rota para o painel administrativo
    path('', views.home, name='home'),  # Página inicial
	
]
