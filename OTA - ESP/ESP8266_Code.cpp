#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoOTA.h>

// === Configurações de rede ===
const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

// === Configuração do servidor remoto ===
const String url = "https://meusite.com/api/comando"; // Substituir pela URL do site

// === Controle da saída ===
const int pino_saida = 2;
bool saida_ligada = false;
unsigned long tempo_ligado = 0;
const unsigned long TEMPO_MAXIMO = 3000; // 3 segundos

// === Temporização da consulta HTTP ===
const unsigned long intervalo_requisicao = 5000; // 5 segundos
unsigned long ultimo_tempo = 0;

void setup() {
  Serial.begin(115200);
  pinMode(pino_saida, OUTPUT);
  digitalWrite(pino_saida, LOW);

  // Conectar ao Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Configurar OTA
  ArduinoOTA
    .onStart([]() {
      Serial.println("Iniciando OTA...");
    })
    .onEnd([]() {
      Serial.println("\nOTA finalizado!");
    })
    .onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progresso: %u%%\r", (progress * 100) / total);
    })
    .onError([](ota_error_t error) {
      Serial.printf("Erro OTA[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Erro de autenticação");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Erro ao iniciar");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Erro de conexão");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Erro de recebimento");
      else if (error == OTA_END_ERROR) Serial.println("Erro ao finalizar");
    });

  ArduinoOTA.begin();
  Serial.println("Pronto para OTA");
}

void loop() {
  // Verifica atualizações OTA
  ArduinoOTA.handle();

  unsigned long agora = millis();

  // Consulta o servidor a cada intervalo definido
  if (agora - ultimo_tempo >= intervalo_requisicao) {
    ultimo_tempo = agora;

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(url);
      int httpCode = http.GET();

      if (httpCode == 200) {
        String comando = http.getString();
        comando.trim(); // Remove espaços e quebras de linha
        Serial.println("Comando recebido: " + comando);

        if (comando == "ligar") {
          digitalWrite(pino_saida, HIGH);
          tempo_ligado = agora;
          saida_ligada = true;
        } else if (comando == "desligar") {
          digitalWrite(pino_saida, LOW);
          saida_ligada = false;
        }
      } else {
        Serial.println("Erro HTTP: " + String(httpCode));
      }

      http.end();
    } else {
      Serial.println("Wi-Fi desconectado.");
    }
  }

  // Desligamento automático após 3 segundos
  if (saida_ligada && (millis() - tempo_ligado >= TEMPO_MAXIMO)) {
    digitalWrite(pino_saida, LOW);
    saida_ligada = false;
    Serial.println("Saída desligada automaticamente.");
  }
}