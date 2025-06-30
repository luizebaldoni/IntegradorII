/*
  SISTEMA DE SIRENE ESCOLAR - FIRMWARE ESP8266

  DESCRIÇÃO:
  Este firmware controla um dispositivo ESP8266 que:
  - Conecta-se à rede WiFi
  - Sincroniza horário via NTP
  - Consulta agendamentos no servidor Django
  - Ativa/desativa saída digital conforme agendamento

  FUNCIONALIDADES:
  - Atualização OTA (Over-The-Air)
  - Sincronização de horário preciso
  - Controle de saída com timeout de segurança
  - Logs detalhados via Serial

  CONFIGURAÇÃO:
  - Definir credenciais WiFi
  - Definir URL do servidor Django
  - Configurar pino de saída
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

// ========= CONFIGURAÇÕES ========= //
const char* ssid = "Hidrogenio_2.4";        // SSID da rede Wi-Fi à qual o ESP8266 se conectará
const char* password = "ceespsol";             // Senha da rede Wi-Fi
const String serverUrl = "http://192.168.1.40:8000/api/comando"; // URL do servidor Django

const int outputPin = 5;           // Pino de controle da sirene
const unsigned long outputTimeout = 1000; // Tempo máximo de ativação (ms)
const unsigned long requestInterval = 10000; // Intervalo entre requisições (ms)

// ========= VARIÁVEIS GLOBAIS ========= //
bool outputState = false;
unsigned long outputStartTime = 0;
unsigned long lastRequestTime = 0;
int lastActivatedMinute = -1; // Armazena o último minuto de ativação

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "br.pool.ntp.org", -3 * 3600);  // UTC-3 (Brasília)

// Mapeamento de dias da semana
const char* DAYS_OF_WEEK[7] = {"DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"};

void setup() {
  Serial.begin(115200);
  pinMode(outputPin, OUTPUT);
  digitalWrite(outputPin, LOW);

  connectWiFi();
  setupOTA();
  setupNTP();

  Serial.println("Sistema iniciado");
}

void loop() {
  ArduinoOTA.handle();
  timeClient.update();

  unsigned long currentMillis = millis();

  // Verifica timeout da saída
  if (outputState && (currentMillis - outputStartTime >= outputTimeout)) {
    deactivateOutput();
  }

  // Faz requisições periódicas ao servidor
  if (currentMillis - lastRequestTime >= requestInterval) {
    lastRequestTime = currentMillis;

    if (WiFi.status() == WL_CONNECTED) {
      checkSchedules();
    } else {
      Serial.println("WiFi desconectado, tentando reconectar...");
      connectWiFi();
    }
  }
}

void connectWiFi() {
  Serial.print("Conectando ao WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
}

void setupOTA() {
  ArduinoOTA.onStart([]() {
    Serial.println("Início da atualização OTA");
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nAtualização OTA concluída!");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progresso: %u%%\r", (progress * 100) / total);
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Erro OTA [%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Autenticação falhou");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Falha ao iniciar");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Falha na conexão");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Falha na recepção");
    else if (error == OTA_END_ERROR) Serial.println("Falha ao finalizar");
  });

  ArduinoOTA.begin();
  Serial.println("OTA pronto");
}

void setupNTP() {
  timeClient.begin();

  Serial.print("Sincronizando horário NTP...");
  int attempts = 0;
  while (!timeClient.update() && attempts < 10) {
    attempts++;
    delay(1000);
    Serial.print(".");
  }

  if (attempts < 10) {
    Serial.println(" OK!");
    Serial.println("Horário atual: " + timeClient.getFormattedTime());
  } else {
    Serial.println(" Falha na sincronização!");
  }
}

void checkSchedules() {
  HTTPClient http;
  WiFiClient client;

  http.begin(client, serverUrl);
  http.setTimeout(10000);
  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);

    String currentTime = timeClient.getFormattedTime(); // "HH:MM:SS"
    String currentHourMin = currentTime.substring(0, 5); // "HH:MM"
    int currentMinute = timeClient.getMinutes();
    int currentDayIndex = timeClient.getDay(); // 0=Domingo
    String currentDay = DAYS_OF_WEEK[currentDayIndex];

    Serial.println("DEBUG - Horário: " + currentTime + " | Dia: " + currentDay);

    // Verifica a cada 10 segundos (para maior confiabilidade)
    if (timeClient.getSeconds() <= 10 && currentMinute != lastActivatedMinute) {
      JsonArray agendamentos = doc["agendamentos"];
      for (JsonObject ag : agendamentos) {
        String agTime = ag["time"].as<String>(); // "HH:MM"
        String agDays = ag["days_of_week"].as<String>(); // "DOM" ou "SEG,QUA"

        // Verifica se o dia atual está nos dias agendados
        if (agDays.indexOf(currentDay) != -1 && currentHourMin == agTime) {
          activateOutput();
          lastActivatedMinute = currentMinute;
          Serial.println("DEBUG - Acionamento para: " + agTime + " | Dias: " + agDays);
          break;
        }
      }
    }
  } else {
    Serial.println("Erro HTTP: " + String(httpCode));
  }
  http.end();
}

void activateOutput() {
  if (!outputState) {
    Serial.println("Ativando saída...");
    digitalWrite(outputPin, HIGH);
    outputState = true;
    outputStartTime = millis();
  }
}

void deactivateOutput() {
  if (outputState) {
    Serial.println("Desativando saída...");
    digitalWrite(outputPin, LOW);
    outputState = false;
  }
}
