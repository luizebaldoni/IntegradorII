/*
 * CONTROLE REMOTO DE SIRENE COM ESP8266, OTA E AGENDAMENTO JSON
 * Data: 28/06/2025
 *
 * DESCRIÇÃO:
 * Este código utiliza o módulo ESP8266 para conectar-se a uma rede Wi-Fi, consultar um servidor remoto periodicamente
 * e executar comandos de agendamento para controlar uma saída digital (pino 5).
 * Os comandos recebidos do servidor são processados em formato JSON e executados no horário programado.
 * A funcionalidade de OTA (Over-The-Air) também está configurada para permitir atualizações remotas do firmware.
 *
 * APLICAÇÕES:
 * - Controle remoto de sirene via Wi-Fi usando ESP8266
 * - Execução de comandos de agendamento para ligar/desligar dispositivos
 * - Atualizações do firmware via OTA (Over-The-Air)
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoOTA.h>
#include <ArduinoJson.h>  // Biblioteca para manipulação de JSON
#include <TimeLib.h>      // Para trabalhar com hora e data

///// CONFIGURAÇÕES DE REDE ///// 
const char* ssid = "SSID_REDE";      // SSID da rede Wi-Fi à qual o ESP8266 se conectará
const char* password = "SENHA_REDE";           // Senha da rede Wi-Fi

///// CONFIGURAÇÃO DO SERVIDOR REMOTO ///// 
const String url = "http://IP_DO_SERVIDOR:PORTA_SERVIDOR/api/comando"; // URL do servidor que envia os comandos

///// CONTROLE DA SAÍDA ///// 
const int pino_saida = 5;                   // Pino de saída conectado a um dispositivo, como um LED ou relé
bool saida_ligada = false;                  // Flag que indica se a saída está ligada ou desligada
unsigned long tempo_ligado = 0;             // Armazena o tempo em que a saída foi ligada
const unsigned long TEMPO_MAXIMO = 1000;    // Tempo máximo de ativação da saída em milissegundos (3 segundos)

///// VARIÁVEIS PARA AGENDAMENTOS ///// 
int hora_agendamento = -1;                  // Hora de agendamento para execução do comando
int minuto_agendamento = -1;                // Minuto de agendamento para execução do comando
String comando_agendamento = "";            // Comando agendado (ligar/desligar)

///// TEMPORIZAÇÃO DA CONSULTA HTTP ///// 
const unsigned long intervalo_requisicao = 5000; // Intervalo de 5 segundos entre as consultas ao servidor remoto
unsigned long ultimo_tempo = 0;                  // Armazena o tempo da última requisição

///// FUNÇÃO PARA CONECTAR AO WIFI ///// 
void conectarWiFi() {
  WiFi.begin(ssid, password);                  // Inicia a conexão com a rede Wi-Fi usando o SSID e a senha fornecidos
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {      // Aguarda a conexão com o Wi-Fi
    delay(500);
    Serial.print(".");                         // Exibe um ponto a cada meio segundo enquanto tenta conectar
  }
  Serial.println("\nWi-Fi conectado");         // Exibe mensagem confirmando a conexão bem-sucedida
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());              // Exibe o endereço IP atribuído ao ESP8266
}

///// FUNÇÃO PARA CONFIGURAR OTA ///// 
void configurarOTA() {
  ArduinoOTA.onStart([]() {                   // Define o comportamento ao iniciar uma atualização OTA
    Serial.println("Iniciando OTA...");
  });
  ArduinoOTA.onEnd([]() {                     // Define o comportamento ao finalizar uma atualização OTA
    Serial.println("\nOTA finalizado!");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) { // Exibe o progresso da atualização OTA
    Serial.printf("Progresso: %u%%\r", (progress * 100) / total);
  });
  ArduinoOTA.onError([](ota_error_t error) {  // Define o comportamento em caso de erro durante a atualização OTA
    Serial.printf("Erro OTA[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Erro de autenticação");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Erro ao iniciar");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Erro de conexão");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Erro de recebimento");
    else if (error == OTA_END_ERROR) Serial.println("Erro ao finalizar");
  });
  ArduinoOTA.begin();                         // Inicia o processo de OTA
}

///// FUNÇÃO DE INICIALIZAÇÃO ///// 
void setup() {
  Serial.begin(115200);                        // Inicializa a comunicação serial a 115200 bps
  pinMode(pino_saida, OUTPUT);                  // Configura o pino de saída como pino de saída
  digitalWrite(pino_saida, LOW);                // Inicializa a saída com valor baixo (desligado)

  // Conectar ao Wi-Fi
  conectarWiFi();

  // Configurar OTA
  configurarOTA();
  Serial.println("Pronto para OTA");

  // Configurar o relógio (defina a hora corretamente ou use NTP)
  setTime(12, 0, 0, 1, 1, 2025);  // Exemplo: define 12:00:00 em 01/01/2025 (ajuste conforme necessário)
}

///// LOOP PRINCIPAL ///// 
void loop() {
  ArduinoOTA.handle();  // Verifica se há uma atualização OTA em andamento

  unsigned long agora = millis(); // Obtém o tempo atual desde o início do programa

  // Consulta o servidor a cada intervalo definido (5 segundos)
  if (agora - ultimo_tempo >= intervalo_requisicao) {
    ultimo_tempo = agora;  // Atualiza o tempo da última consulta

    // Verifica se o ESP8266 está conectado ao Wi-Fi
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;                  // Cria um objeto HTTPClient para enviar a requisição
      WiFiClient client;                 // Cria um cliente Wi-Fi
      http.begin(client, url);          // Inicia a requisição HTTP com a URL do servidor remoto
      int httpCode = http.GET();        // Envia a requisição GET para o servidor remoto

      // Verifica se a resposta HTTP foi bem-sucedida
      if (httpCode == 200) {
        String payload = http.getString();  // Obtém o payload JSON do servidor
        Serial.println("Recebido JSON: " + payload);

        // Parse do JSON
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, payload);  // Deserializa o JSON recebido

        // Pegando o agendamento (primeiro agendamento para o exemplo)
        JsonArray agendamentos = doc["agendamentos"];
        for (JsonObject agendamento : agendamentos) {
          hora_agendamento = agendamento["hora"];
          minuto_agendamento = agendamento["minuto"];
          comando_agendamento = agendamento["comando"].as<String>(); // Corrige conversão para String

          // Verifica se o horário atual coincide com o agendamento
          int hora_atual = hour();  // Obtém a hora atual
          int minuto_atual = minute();  // Obtém o minuto atual

          Serial.print("Hora Atual: ");
          Serial.print(hora_atual);
          Serial.print(" Minuto Atual: ");
          Serial.println(minuto_atual);

          // Compara o horário atual com o agendamento
          if (hora_atual == hora_agendamento && minuto_atual == minuto_agendamento) {
            if (comando_agendamento == "ligar") {
              digitalWrite(pino_saida, HIGH);  // Liga a saída
              tempo_ligado = agora;            // Registra o tempo de ativação da saída
              saida_ligada = true;             // Atualiza a flag indicando que a saída está ligada
              Serial.println("Comando 'ligar' executado automaticamente");
            } 
            else if (comando_agendamento == "desligar") {
              digitalWrite(pino_saida, LOW);   // Desliga a saída
              saida_ligada = false;            // Atualiza a flag indicando que a saída está desligada
              Serial.println("Comando 'desligar' executado automaticamente");
            }

            // Responder ao servidor que o comando foi executado
            HTTPClient responseHttp;
            responseHttp.begin(client, url); // URL do servidor de resposta
            responseHttp.addHeader("Content-Type", "text/plain");
            responseHttp.POST("Comando Executado");  // Envia resposta confirmando a execução do comando
            responseHttp.end();  // Finaliza a requisição HTTP de resposta
          }
        }
      } else {
        Serial.println("Erro HTTP: " + String(httpCode));  // Exibe o código de erro em caso de falha na requisição HTTP
      }

      http.end();  // Finaliza a requisição HTTP
    } else {
      Serial.println("Wi-Fi desconectado.");  // Informa que o ESP8266 está desconectado da rede Wi-Fi
    }
  }

  // Desligamento automático da saída após 3 segundos de ativação
  if (saida_ligada && (millis() - tempo_ligado >= TEMPO_MAXIMO)) {
    digitalWrite(pino_saida, LOW);  // Desliga a saída após 3 segundos
    saida_ligada = false;           // Atualiza a flag indicando que a saída foi desligada
    Serial.println("Saída desligada automaticamente.");  // Informa no monitor serial que a saída foi desligada
  }
}
