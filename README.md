
# 📣 Sistema de Sirene Escolar IoT

**Solução completa para automação de sirenes em instituições de ensino usando ESP8266 e Django**

---

## 📌 Índice

- [Visão Geral](#-visão-geral)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [API](#-api)
- [Segurança](#-segurança)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Licença](#-licença)

---

## 🌐 Visão Geral

Sistema IoT para controle automatizado de sirenes escolares com:

- ✅ Agendamento inteligente (aulas, recreios, eventos)
- ✅ Ativação remota via interface web
- ✅ Sincronização horária via NTP
- ✅ Logs completos de operação
- ✅ Fail-safes para evitar ativações indevidas

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologias |
|------------|-------------|
| Backend    | Python 3.9+, Django 4.2, Django REST Framework, SQLite |
| Firmware   | C++ (Arduino Core), ESP8266HTTPClient, NTPClient, ArduinoJson |
| Frontend   | HTML5, Bootstrap 5, Chart.js (para gráficos de histórico) |
| Infra      | Gunicorn (produção), Nginx (proxy reverso), Raspberry Pi (opcional) |

```mermaid
graph TD
    %% ===== FRONTEND =====
    FRONTEND["**Frontend**
    - Django Admin
    - index.html"]
    
    %% ===== BACKEND =====
    VIEWS["**views.py**
    - API REST
    - data_receiver"]
    MODELS["**models.py**
    - Device
    - AlarmSchedule"]
    LOGIC["**views.py & forms.py**
    - Motor de Regras"]
    
    %% ===== BANCO =====
    DB[("**SQLite3**
    - Device
    - AlarmSchedule
    - DeviceLog
    - SensorData")]
    
    %% ===== HARDWARE =====
    ESP["**ESP8266**
    - WiFi Manager
    - JSON Parser"]
    SIRENE["**Sirene Física**
    - Buzzer
    - LOW or HIGH"]
    
    %% ===== FLUXO =====
    FRONTEND -->|HTTP| VIEWS
    VIEWS -->|ORM| MODELS
    MODELS --> DB
    VIEWS -->|HTTP JSON| ESP
    ESP -->|GPIO| SIRENE
    SIRENE -->|ESTADO| ESP
    ESP -->|HTTP Logs| VIEWS
    LOGIC --> VIEWS

```

---
## Banco de Dados

```mermaid
erDiagram
    %% ========== MODELOS PRINCIPAIS ==========
    DEVICE {
        string device_id PK
        string device_name
        datetime last_seen
        string status
    }

    SENSOR {
        int id PK
        string name
        string sensor_type
        float value
        datetime timestamp
    }

    SENSOR_DATA {
        int id PK
        float value
        datetime timestamp
    }

    DEVICE_CONFIG {
        int id PK
        int send_interval
        float temp_threshold
    }

    %% ========== CONTROLE DE SIRENE ==========
    COMANDO_ESP {
        int id PK
        string comando
        string source
        boolean executado
        datetime timestamp
    }

    SIREN_STATUS {
        int id PK
        boolean is_on
        datetime last_activated
    }

    ALARM_SCHEDULE {
        int id PK
        boolean active
        string event_type
        time time
        string days_of_week
        date start_date
        date end_date
        datetime created_at
        datetime updated_at
    }

    %% ========== CONFIGURAÇÕES E LOGS ==========
    GLOBAL_CONFIG {
        int id PK
        string api_key
        int data_refresh_interval
    }

    DEVICE_LOG {
        int id PK
        text log_message
        datetime timestamp
    }

    %% ========== RELACIONAMENTOS CORRIGIDOS ==========
    DEVICE ||--o{ SENSOR_DATA : "gera"
    DEVICE ||--|| DEVICE_CONFIG : "possui"
    DEVICE ||--o{ DEVICE_LOG : "registra"
    SENSOR ||--o{ SENSOR_DATA : "contém"
    ALARM_SCHEDULE ||--|{ COMANDO_ESP : "dispara"
    COMANDO_ESP ||--|| SIREN_STATUS : "atualiza"


```

## 🏗️ Arquitetura do Sistema

```mermaid
graph TD
    %% ========== ESTILOS ==========
    classDef user fill:#ffffff,stroke:#2c3e50
    classDef frontend fill:#eaf2f8,stroke:#2980b9
    classDef backend fill:#e8f8f5,stroke:#27ae60
    classDef device fill:#fdedec,stroke:#e74c3c
    classDef data fill:#fff3cd,stroke:#f39c12

    %% ========== PARTICIPANTES ==========
    USUARIO[["Usuário"]]:::user
    FRONTEND[["Interface Web<br/>(Django)"]]:::frontend
    BACKEND[["Servidor Django<br/>(manage.py)"]]:::backend
    ESP8266[["Microcontrolador<br/>(ESP8266)"]]:::device
    SIREINE[["Sirene"]]:::device

    %% ========== DADOS ==========
    JSON_AGENDA[["JSON de Agenda"]]:::data
    DB[["Banco de Dados<br/>(SQLite3)"]]:::data

    %% ========== FLUXO COMPLETO ==========
    USUARIO -->|Configura agenda| FRONTEND
    FRONTEND -->|Salva configuração| DB
    BACKEND -->|Gera JSON| JSON_AGENDA
    BACKEND -->|Envia via API REST| ESP8266
    ESP8266 -->|Interpreta JSON| JSON_AGENDA
    JSON_AGENDA -->|Verifica horário| ESP8266
    ESP8266 -->|Ativa/Desativa| SIREINE
    SIREINE -->|Feedback| ESP8266
    ESP8266 -->|Log de estado| BACKEND
    BACKEND -->|Atualiza status| DB

    %% ========== ESTILOS DE LINHA ==========
    linkStyle 3 stroke:#9b59b6,stroke-width:2px,stroke-dasharray:5
    linkStyle 6 stroke:#e74c3c,stroke-width:2px


```
---

## 📥 Instalação

### Pré-requisitos

- Python 3.9+
- Arduino IDE (para firmware)
- ESP8266 com WiFi

### Backend (Django)

```bash
git clone [repo_url]
cd sirene-escolar
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Firmware (ESP8266)

1. Instale as bibliotecas no Arduino IDE:
   - ESP8266HTTPClient
   - NTPClient
   - ArduinoJson

2. Carregue `ESP8266_Code.cpp`

3. Configure `settings.h` com suas credenciais WiFi

---

## ⚙️ Configuração

### Arquivo `settings.py` (Django)

```python
# Configurações críticas
ALLOWED_HOSTS = ['*']  # Restrinja em produção!
TIME_ZONE = 'America/Sao_Paulo'
```

### Hardware

| Componente | Pino ESP8266 | Observações |
|------------|--------------|-------------|
| Sirene     | GPIO5 (D1)   | Relay ou transistor |
| LED Status | GPIO2 (D4)   | LED interno (invertido) |

---

## 🚀 Como Usar

### 1. Agendamentos

Acesse `http://localhost:8000/admin` e:

- Crie um novo `AlarmSchedule`
- Defina:
  - Tipo de evento (Aula, Recreio, etc.)
  - Horário e dias da semana
  - Período de validade

### 2. Ativação Manual

```bash
curl -X POST http://localhost:8000/ativar/   -H "Content-Type: application/json"   -d '{}'
```

### 3. Monitoramento

- **Serial Monitor**: Logs do ESP (115200 baud)
- **Admin Django**: Histórico em `DeviceLog`

---

## 📡 Documentação da API

| Endpoint           | Método | Parâmetros               | Resposta                |
|--------------------|--------|--------------------------|-------------------------|
| `/api/comando`     | GET    | -                        | JSON com agendamentos   |
| `/check_command/`  | GET    | -                        | `{"command": "ligar"}`  |
| `/confirm_command/`| POST   | `{"status": "success"}`  | -                       |
| `/api/sensor_data` | POST   | `{"value": 25.5, "type": "temp"}` | Log no banco de dados |

---

## 🔒 Segurança

### Medidas Atuais

- Timeout automático de 3s na sirene
- Verificação de duplicidade de comandos

### Recomendações para Produção

- Implementar HTTPS
- Adicionar autenticação JWT
- Restringir `ALLOWED_HOSTS`
- Usar PostgreSQL com criptografia

---

## 🐛 Troubleshooting

| Problema                 | Solução                        |
|--------------------------|--------------------------------|
| ESP não conecta ao WiFi  | Verificar credenciais e sinal  |
| Horário incorreto        | Checar servidor NTP e fuso horário |
| Sirene não desliga       | Testar circuito de potência/relay |
| API retorna 403          | Checar CSRF tokens ou CORS    |

---

## 🛣️ Roadmap e Ideias para Melhorias Futuras

- App móvel para notificações
- Integração com calendário acadêmico
- Dashboard com métricas em tempo real
- Suporte a múltiplas sirenes

---

## 📜 Licença

MIT License - Consulte o arquivo LICENSE para detalhes.

Documentação completa disponível em `/docs/`.
