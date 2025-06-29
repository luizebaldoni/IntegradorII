/*
 * SISTEMA DE SIRENE ESCOLAR - FIRMWARE ESP8266
 * Data: 28/06/2025
 *
 * DESCRIÇÃO:
 * Este firmware controla um dispositivo ESP8266 que:
 * - Conecta-se à rede WiFi
 * - Sincroniza horário via NTP
 * - Consulta agendamentos no servidor Django
 * - Ativa/desativa a saída digital conforme agendamento
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
#include <ArduinoOTA.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

///// CONFIGURAÇÕES DE REDE /////
const char* ssid = "SSID";        // SSID da rede Wi-Fi à qual o ESP8266 se conectará
const char* password = "SENHA";             // Senha da rede Wi-Fi
const String serverUrl = "http://IP:PORTA/api/comando"; // URL do servidor Django

///// CONFIGURAÇÃO DO PINO DE SAÍDA E TIMEOUT /////
const int outputPin = 5;                         // Pino de controle da sirene (saída digital)
const unsigned long outputTimeout = 1000;        // Tempo máximo de ativação da sirene (1 segundo)
const unsigned long requestInterval = 30000;     // Intervalo entre requisições ao servidor (30 segundos)

///// VARIÁVEIS GLOBAIS /////
bool outputState = false;                        // Estado atual da saída (ligado ou desligado)
unsigned long outputStartTime = 0;               // Armazena o tempo em que a saída foi ativada
unsigned long lastRequestTime = 0;               // Armazena o tempo da última requisição ao servidor

WiFiUDP ntpUDP;                                  // Objeto UDP para comunicação com o servidor NTP
NTPClient timeClient(ntpUDP, "pool.ntp.org", -3 * 3600);  // Cliente NTP configurado para UTC-3 (Brasília)

///// FUNÇÃO DE INICIALIZAÇÃO /////
void setup() {
  Serial.begin(115200);                          // Inicializa a comunicação serial a 115200 bps
  pinMode(outputPin, OUTPUT);                    // Configura o pino de saída como saída digital
  digitalWrite(outputPin, LOW);                  // Inicializa a saída com valor baixo (sirene desligada)

  connectWiFi();                                // Conecta-se à rede Wi-Fi
  setupOTA();                                   // Configura a funcionalidade de OTA (Over-The-Air)
  setupNTP();                                   // Configura e sincroniza o horário via NTP

  Serial.println("Sistema iniciado");
}

///// LOOP PRINCIPAL /////
void loop() {
  ArduinoOTA.handle();                          // Verifica atualizações OTA pendentes
  timeClient.update();                          // Atualiza o horário sincronizado via NTP

  unsigned long currentMillis = millis();      // Obtém o tempo atual desde o início do programa

  // Verifica timeout da saída (desliga a sirene após o tempo limite)
  if (outputState && (currentMillis - outputStartTime >= outputTimeout)) {
    deactivateOutput();                         // Desliga a saída automaticamente após o timeout
  }

  // Faz requisições periódicas ao servidor para verificar agendamentos
  if (currentMillis - lastRequestTime >= requestInterval) {
    lastRequestTime = currentMillis;           // Atualiza o tempo da última requisição

    if (WiFi.status() == WL_CONNECTED) {       // Verifica se o ESP8266 está conectado ao Wi-Fi
      checkSchedules();                         // Consulta o servidor para obter agendamentos
    } else {
      Serial.println("WiFi desconectado, tentando reconectar...");
      connectWiFi();                           // Tenta reconectar ao Wi-Fi se desconectado
    }
  }
}

///// FUNÇÃO DE CONEXÃO COM Wi-Fi /////
void connectWiFi() {
  Serial.print("Conectando ao WiFi...");
  WiFi.begin(ssid, password);                  // Inicia a conexão com a rede Wi-Fi

  while (WiFi.status() != WL_CONNECTED) {      // Aguarda a conexão com o Wi-Fi
    delay(500);
    Serial.print(".");                         // Exibe um ponto a cada meio segundo enquanto tenta conectar
  }

  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());  // Exibe o IP após a conexão bem-sucedida
}

///// FUNÇÃO DE CONFIGURAÇÃO OTA (Over-The-Air) /////
void setupOTA() {
  ArduinoOTA.onStart([]() {                   // Define o comportamento ao iniciar uma atualização OTA
    Serial.println("Início da atualização OTA");
  });

  ArduinoOTA.onEnd([]() {                     // Define o comportamento ao finalizar uma atualização OTA
    Serial.println("\nAtualização OTA concluída!");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) { // Exibe o progresso da atualização OTA
    Serial.printf("Progresso: %u%%\r", (progress * 100) / total);
  });

  ArduinoOTA.onError([](ota_error_t error) {  // Define o comportamento em caso de erro durante a atualização OTA
    Serial.printf("Erro OTA [%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Autenticação falhou");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Falha ao iniciar");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Falha na conexão");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Falha na recepção");
    else if (error == OTA_END_ERROR) Serial.println("Falha ao finalizar");
  });

  ArduinoOTA.begin();                         // Inicia o processo de OTA
  Serial.println("OTA pronto");
}

///// FUNÇÃO DE CONFIGURAÇÃO E SINCRONIZAÇÃO DE HORA (NTP) /////
void setupNTP() {
  timeClient.begin();                         // Inicia a sincronização com o servidor NTP

  Serial.print("Sincronizando horário NTP...");
  int attempts = 0;
  while (!timeClient.update() && attempts < 10) {  // Tenta sincronizar o horário até 10 tentativas
    attempts++;
    delay(1000);
    Serial.print(".");                       // Exibe ponto enquanto tenta sincronizar
  }

  if (attempts < 10) {
    Serial.println(" OK!");                  // Exibe sucesso na sincronização
    Serial.println("Horário atual: " + timeClient.getFormattedTime());
  } else {
    Serial.println(" Falha na sincronização!");  // Exibe erro caso falhe na sincronização
  }
}

///// FUNÇÃO DE CONSULTA DE AGENDAMENTOS NO SERVIDOR /////
void checkSchedules() {
  HTTPClient http;
  WiFiClient client;
  http.begin(client, serverUrl);             // Inicia a requisição HTTP ao servidor Django
  int httpCode = http.GET();                 // Envia a requisição GET ao servidor

  if (httpCode == HTTP_CODE_OK) {            // Verifica se a resposta foi bem-sucedida (código HTTP 200)
    String payload = http.getString();       // Obtém o conteúdo da resposta (JSON)
    Serial.println("Resposta da API: " + payload);

    DynamicJsonDocument doc(1024);            // Cria um documento JSON para parsear a resposta
    deserializeJson(doc, payload);           // Deserializa o JSON recebido

    // Exibe a hora do servidor e a hora local
    Serial.println("Hora do servidor: " + doc["current_time"].as<String>());
    Serial.println("Hora local ESP: " + timeClient.getFormattedTime());

    // Verifica os agendamentos e executa os comandos de acordo
    JsonArray agendamentos = doc["agendamentos"];
    if (agendamentos.size() == 0) {
      Serial.println("Nenhum agendamento encontrado para hoje!");
    }
  }
  http.end();  // Finaliza a requisição HTTP
}

///// FUNÇÃO PARA ATIVAR A SAÍDA /////
void activateOutput() {
  if (!outputState) {
    Serial.println("Ativando saída...");
    digitalWrite(outputPin, HIGH);           // Liga a saída (sirene)
    outputState = true;                      // Atualiza o estado da saída para ligado
    outputStartTime = millis();              // Registra o tempo de ativação da saída
  }
}

///// FUNÇÃO PARA DESATIVAR A SAÍDA /////
void deactivateOutput() {
  if (outputState) {
    Serial.println("Desativando saída...");
    digitalWrite(outputPin, LOW);            // Desliga a saída (sirene)
    outputState = false;                     // Atualiza o estado da saída para desligado
  }
}
