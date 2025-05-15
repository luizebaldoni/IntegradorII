#include <WiFi.h>
#include <ArduinoOTA.h>

const char* ssid = "rede";
const char* password = "senha";

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

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
  ArduinoOTA.handle(); // Verifica OTA
}
