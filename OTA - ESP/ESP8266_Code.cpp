/*
 * SISTEMA DE SIRENE ESCOLAR - FIRMWARE ESP8266
 * Engenharia de Computação – UFSM
 * Data: 30/06/2025
 *
 * DESCRIÇÃO:
 * Este firmware controla um dispositivo ESP8266 que:
 * - Conecta-se à rede WiFi
 * - Sincroniza horário via NTP
 * - Consulta agendamentos no servidor Django
 * - Ativa/desativa saída digital conforme agendamento
 *
 * FUNCIONALIDADES:
 * - Atualização OTA (Over-The-Air)
 * - Sincronização de horário preciso
 * - Controle de saída com timeout de segurança
 * - Logs detalhados via Serial
 *
 * CONFIGURAÇÃO:
 * - Definir credenciais WiFi
 * - Definir URL do servidor Django
 * - Configurar pino de saída
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

///// CONFIGURAÇÕES DE REDE /////
const char* ssid = "Hidrogenio_2.4";        // SSID da rede Wi-Fi à qual o ESP8266 se conectará
const char* password = "ceespsol";           // Senha da rede Wi-Fi

// Endpoints do servidor Django
const char* scheduleUrl = "http://192.168.1.40:8000/api/comando"; // URL para verificar agendamentos
const char* commandUrl = "http://192.168.1.40:8000/check_command/"; // URL para comandos manuais
const char* confirmUrl = "http://192.168.1.40:8000/confirm_command/"; // URL para confirmar comando

// Configurações de hardware
const int sirenPin = 5;           // Pino de controle da sirene
const int statusLed = 2;          // LED interno (azul)

///// INTERVALOS DE VERIFICAÇÃO /////
const unsigned long scheduleCheckInterval = 30000;  // 30s para verificar agendamentos
const unsigned long commandCheckInterval = 5000;    // 5s para comandos manuais
const unsigned long sirenMinDuration = 5000;        // Duração mínima da sirene (5s)
const unsigned long sirenMaxDuration = 30000;       // Duração máxima da sirene (30s)

///// VARIÁVEIS GLOBAIS /////
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "br.pool.ntp.org", -3 * 3600);  // UTC-3 (Brasília)

unsigned long lastScheduleCheck = 0;
unsigned long lastCommandCheck = 0;
unsigned long sirenStartTime = 0;
bool sirenActive = false;
String lastCommandId = "";
int wifiRetries = 0;

const char* DAYS_OF_WEEK[7] = {"DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"}; // Mapeamento dos dias da semana

///// FUNÇÃO DE INICIALIZAÇÃO /////
void setup() {
  Serial.begin(115200);
  Serial.println("\nIniciando sistema de sirene escolar...");

  // Configuração dos pinos
  pinMode(sirenPin, OUTPUT);
  pinMode(statusLed, OUTPUT);
  digitalWrite(sirenPin, LOW);
  digitalWrite(statusLed, HIGH); // LED interno (ativo baixo)

  // Conectar ao WiFi
  connectWiFi();

  // Configurar NTP
  setupNTP();

  Serial.println("Sistema pronto");
}

///// LOOP PRINCIPAL /////
void loop() {
  // Atualiza o cliente NTP
  timeClient.update();

  // Handle WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    handleWiFiDisconnection();
  }

  unsigned long currentMillis = millis();

  // 1. Controle de tempo da sirene
  if (sirenActive) {
    // Desativa após o tempo máximo (segurança)
    if (currentMillis - sirenStartTime >= sirenMaxDuration) {
      deactivateSiren("timeout_seguranca");
    }
  }

  // 2. Verificação de agendamentos (menos frequente)
  if (currentMillis - lastScheduleCheck >= scheduleCheckInterval) {
    lastScheduleCheck = currentMillis;
    if (WiFi.status() == WL_CONNECTED) {
      checkSchedules();
    }
  }

  // 3. Verificação de comandos manuais (mais frequente)
  if (currentMillis - lastCommandCheck >= commandCheckInterval) {
    lastCommandCheck = currentMillis;
    if (WiFi.status() == WL_CONNECTED) {
      checkManualCommands();
    }
  }

  // Piscar LED indicativo
  static unsigned long lastBlink = 0;
  if (currentMillis - lastBlink >= 1000) {
    lastBlink = currentMillis;
    digitalWrite(statusLed, !digitalRead(statusLed));
  }
}

///// FUNÇÕES DE CONEXÃO /////

void connectWiFi() {
  Serial.print("Conectando ao WiFi ");
  Serial.print(ssid);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
    wifiRetries = 0;
    digitalWrite(statusLed, LOW); // LED ligado
  } else {
    Serial.println("\nFalha na conexão WiFi");
    digitalWrite(statusLed, HIGH); // LED desligado
  }
}

void handleWiFiDisconnection() {
  wifiRetries++;
  Serial.print("WiFi desconectado. Tentativa ");
  Serial.println(wifiRetries);

  if (wifiRetries > 10) {
    Serial.println("Reiniciando ESP...");
    ESP.restart();
  }

  WiFi.disconnect();
  delay(1000);
  connectWiFi();
}

void setupNTP() {
  timeClient.begin();
  Serial.print("Sincronizando horário NTP...");

  int attempts = 0;
  while (!timeClient.update() && attempts < 10) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (attempts < 10) {
    Serial.println(" OK!");
    Serial.println("Horário atual: " + timeClient.getFormattedTime());
  } else {
    Serial.println(" Falha!");
  }
}

///// FUNÇÕES PRINCIPAIS /////

void checkSchedules() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, scheduleUrl);
  http.setTimeout(10000); // Timeout de 10 segundos

  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);

    bool shouldActivate = doc["should_activate"];
    bool isScheduled = doc["is_scheduled"];

    if (shouldActivate && !sirenActive) {
      String activationSource = isScheduled ? "agendamento" : "servidor";
      activateSiren(activationSource);
    }

    // Log de status
    Serial.print("Status: ");
    Serial.print(shouldActivate ? "ATIVAR" : "DESATIVAR");
    Serial.print(isScheduled ? " (agendado)" : " (manual)");
    Serial.print(" | Hora: ");
    Serial.println(timeClient.getFormattedTime());

    // Debug: próximo alarme
    if (doc.containsKey("next_alarm")) {
      Serial.print("Próximo alarme: ");
      Serial.println(doc["next_alarm"].as<String>());
    }
  } else {
    Serial.print("Erro ao verificar agendamentos: ");
    Serial.println(httpCode);
  }

  http.end();
}

void checkManualCommands() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, commandUrl);
  http.setTimeout(5000); // Timeout de 5 segundos

  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    DynamicJsonDocument doc(256);
    deserializeJson(doc, payload);

    String command = doc["command"];
    if (command == "ligar") {
      String source = doc["source"];
      String commandId = doc["id"];

      if (commandId != lastCommandId) {
        lastCommandId = commandId;
        if (!sirenActive) {
          activateSiren("manual (" + source + ")");
        }
        confirmCommandExecution();
      }
    }
  } else if (httpCode != -1) { // Ignora erros de timeout
    Serial.print("Erro ao verificar comandos: ");
    Serial.println(httpCode);
  }

  http.end();
}

void confirmCommandExecution() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, confirmUrl);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST("{}");

  if (httpCode == HTTP_CODE_OK) {
    Serial.println("Comando manual confirmado no servidor");
  } else {
    Serial.print("Erro ao confirmar comando: ");
    Serial.println(httpCode);
  }

  http.end();
}

///// CONTROLE DA SIRENE /////

void activateSiren(String source) {
  digitalWrite(sirenPin, HIGH);
  sirenActive = true;
  sirenStartTime = millis();

  Serial.print("Sirene ATIVADA por ");
  Serial.print(source);
  Serial.print(" às ");
  Serial.println(timeClient.getFormattedTime());

  // LED fica fixo ligado durante ativação
  digitalWrite(statusLed, LOW);
}

void deactivateSiren(String reason) {
  digitalWrite(sirenPin, LOW);
  sirenActive = false;

  Serial.print("Sirene DESATIVADA (");
  Serial.print(reason);
  Serial.print(") às ");
  Serial.println(timeClient.getFormattedTime());

  // Retorna ao estado normal do LED
  digitalWrite(statusLed, HIGH);
}

///// FUNÇÕES AUXILIARES /////

void printDebugInfo() {
  Serial.println("\n=== DEBUG INFO ===");
  Serial.println("Horário atual: " + timeClient.getFormattedTime());
  Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado"));
  Serial.println("IP: " + WiFi.localIP().toString());
  Serial.println("Sirene: " + String(sirenActive ? "ATIVA" : "INATIVA"));
  Serial.println("Último comando ID: " + lastCommandId);
  Serial.println("==================\n");
}
