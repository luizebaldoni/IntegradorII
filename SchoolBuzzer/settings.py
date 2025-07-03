"""
ARQUIVO DE CONFIGURAÇÃO DJANGO (settings.py)

DESCRIÇÃO:
Este arquivo define todas as configurações centrais do projeto Django "SchoolBuzzer",
incluindo:
- Configuração de diretórios, segurança, banco de dados e internacionalização
- Definição das aplicações instaladas
- Configurações específicas da sirene escolar com ESP

ATENÇÃO:
Este projeto utiliza ESP_BELL_URL para comunicação com ESP8266.
"""

# ========================================================
# IMPORTAÇÕES E CONFIGURAÇÃO DE DIRETÓRIOS
# ========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Diretório base do projeto

# ========================================================
# SEGURANÇA E AMBIENTE
# ========================================================

SECRET_KEY = 'django-insecure-d@&jygktz+i@rt$022uw_$(+11wr8#tsnsjo9%#d5j23i4$qdj'
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.40',  # ← IP local da máquina para acesso via ESP
]

# ========================================================
# APLICAÇÕES INSTALADAS
# ========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # API REST
    'app',             # Aplicação principal do sistema de sirene
]

# ========================================================
# MIDDLEWARE (PILHAS DE PROCESSAMENTO)
# ========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================================================
# CONFIGURAÇÃO DE URLs E TEMPLATES
# ========================================================

ROOT_URLCONF = 'SchoolBuzzer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Diretório de templates personalizados
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SchoolBuzzer.wsgi.application'

# ========================================================
# BANCO DE DADOS
# ========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========================================================
# VALIDAÇÃO DE SENHAS
# ========================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================================================
# LOCALIZAÇÃO E FUSO HORÁRIO
# ========================================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ========================================================
# ARQUIVOS ESTÁTICOS (CSS, JS, IMAGENS)
# ========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Diretório de arquivos estáticos do projeto
]

# ========================================================
# CONFIGURAÇÕES DO SISTEMA DE SIRENE
# ========================================================

ESP_BELL_URL = "http://192.168.1.14/ring"  # Endereço da ESP8266 (POST de comando)

# ========================================================
# LOGGING (EXIBIÇÃO NO TERMINAL)
# ========================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# ========================================================
# CONFIGURAÇÃO PADRÃO PARA CHAVE PRIMÁRIA
# ========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
