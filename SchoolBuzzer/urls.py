from django.contrib import admin
from django.urls import path, include

"""
CONFIGURAÇÃO DE ROTAS PRINCIPAIS – SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo define as rotas principais da aplicação Django, integrando o painel administrativo
padrão e todas as rotas definidas no aplicativo principal (app.urls).

ROTAS DEFINIDAS:
- /admin/ : acesso ao painel administrativo Django
- /       : redirecionamento para as rotas do aplicativo principal
"""

urlpatterns = [
		path('admin/', admin.site.urls),
		path('', include(('app.urls', 'app'), namespace = 'app')),  # ← CORRETO
]
