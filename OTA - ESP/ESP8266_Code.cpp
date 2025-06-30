/*
 * SISTEMA DE SIRENE ESCOLAR - FIRMWARE ESP8266
 * Engenharia de Computação – UFSM
 * Data: 30/06/2025
 *
 * DESCRIÇÃO:
 * Este firmware foi desenvolvido para controlar um dispositivo baseado em ESP8266,
 * permitindo a integração com um sistema de gerenciamento remoto via servidor Django.
 * O sistema realiza as seguintes funções:
 * - Conexão com a rede WiFi local para comunicação com a internet.
 * - Sincronização de horário com um servidor NTP (Network Time Protocol) para garantir
 *   que o dispositivo tenha o horário correto.
 * - Consulta de agendamentos de comandos através de um servidor Django para ativação
 *   ou desativação da sirene de forma programada.
 * - Ativação/desativação de saída digital (controle de sirene) conforme o agendamento
 *   ou comandos manuais.
 *
 * FUNCIONALIDADES:
 * - **Atualização OTA (Over-The-Air)**: Permite atualizar o firmware do dispositivo sem
 *   a necessidade de uma conexão física.
 * - **Sincronização de horário preciso**: Usa o protocolo NTP para obter o horário atual
 *   de um servidor remoto.
 * - **Controle de saída com timeout de segurança**: A sirene é desativada automaticamente
 *   após um tempo máximo de ativação para evitar funcionamento contínuo e prolongado.
 * - **Logs detalhados via Serial**: Exibe informações sobre o estado do sistema e
 *   processos de ativação/desativação da sirene para depuração e controle.
 *
 * CONFIGURAÇÃO:
 * - **WiFi**: Definir as credenciais da rede Wi-Fi para o dispositivo se conectar à rede
 *   local.
 * - **Servidor Django**: Definir a URL do servidor que irá fornecer os agendamentos e
 *   comandos manuais para controle da sirene.
 * - **Pino de saída**: Configurar o pino digital responsável por controlar a sirene.
 *
 * FUNCIONAMENTO:
 * O firmware está configurado para:
 * 1. Conectar-se automaticamente à rede WiFi.
 * 2. Sincronizar a hora com um servidor NTP.
 * 3. Realizar requisições periódicas ao servidor Django para verificar agendamentos
 *    e comandos manuais.
 * 4. Ativar ou desativar a sirene de acordo com os agendamentos recebidos ou comandos
 *    manuais via API.
 * 5. Desativar automaticamente a sirene após um tempo limite de segurança, evitando
 *    o funcionamento contínuo.
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
const int sirenPin = 5;           // Pino de controle da sirene (saída digital, D1 no ESP8266)
const int statusLed = 2;          // LED interno (azul, D4 no ESP8266)

///// INTERVALOS DE VERIFICAÇÃO /////
const unsigned long scheduleCheckInterval = 100000;  // Intervalo de 1 minuto para verificar agendamentos
const unsigned long commandCheckInterval = 5000;    // Intervalo de 5 segundos para verificar comandos manuais
const unsigned long sirenMinDuration = 2000;        // Duração mínima da sirene (2 segundos)
const unsigned long sirenMaxDuration = 5000;       // Duração máxima da sirene (5 segundos)

///// VARIÁVEIS GLOBAIS /////
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "br.pool.ntp.org", -3 * 3600);  // UTC-3 (Brasília)

unsigned long lastScheduleCheck = 0;    // Marca o último tempo que a consulta ao servidor de agendamentos foi realizada
unsigned long lastCommandCheck = 0;     // Marca o último tempo que a consulta ao servidor de comandos manuais foi realizada
unsigned long sirenStartTime = 0;       // Marca o momento que a sirene foi ativada
bool sirenActive = false;               // Estado da sirene (ativada ou desativada)
String lastCommandId = "";              // Armazena o ID do último comando manual recebido
int wifiRetries = 0;                    // Contador de tentativas de reconexão Wi-Fi

const char* DAYS_OF_WEEK[7] = {"DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"}; // Mapeamento dos dias da semana

///// FUNÇÃO DE INICIALIZAÇÃO /////
void setup() {
  Serial.begin(115200);                          // Inicializa a comunicação serial com a taxa de 115200 bps
  Serial.println("\nIniciando sistema de sirene escolar...");

  // Configuração dos pinos
  pinMode(sirenPin, OUTPUT);                     // Configura o pino da sirene como saída digital
  pinMode(statusLed, OUTPUT);                    // Configura o pino do LED interno como saída digital
  digitalWrite(sirenPin, LOW);                   // Inicializa a sirene desligada
  digitalWrite(statusLed, LOW);                  // LED interno desligado (ativo baixo)

  // Conectar ao WiFi
  connectWiFi();

  // Configurar NTP (Network Time Protocol)
  setupNTP();

  Serial.println("Sistema pronto");
}

///// LOOP PRINCIPAL /////
void loop() {
  // Atualiza o cliente NTP
  timeClient.update();

  // Verifica conexão com WiFi
  if (WiFi.status() != WL_CONNECTED) {
    handleWiFiDisconnection();
  }

  unsigned long currentMillis = millis();     // Obtém o tempo atual desde que o dispositivo foi iniciado

  // 1. Controle de tempo da sirene
  if (sirenActive) {
    // Desativa após o tempo máximo (segurança)
    if (currentMillis - sirenStartTime >= sirenMaxDuration) {
      deactivateSiren("timeout_seguranca");  // Desliga a sirene automaticamente após o timeout de segurança
    }
  }

  // 2. Verificação de agendamentos (menos frequente)
  if (currentMillis - lastScheduleCheck >= scheduleCheckInterval) {
    lastScheduleCheck = currentMillis;
    if (WiFi.status() == WL_CONNECTED) {
      checkSchedules();  // Verifica os agendamentos no servidor Django
    }
  }

  // 3. Verificação de comandos manuais (mais frequente)
  if (currentMillis - lastCommandCheck >= commandCheckInterval) {
    lastCommandCheck = currentMillis;
    if (WiFi.status() == WL_CONNECTED) {
      checkManualCommands();  // Verifica se há comandos manuais disponíveis
    }
  }

  // Piscar LED indicativo
  static unsigned long lastBlink = 0;
  if (currentMillis - lastBlink >= 1000) {
    lastBlink = currentMillis;
    digitalWrite(statusLed, !digitalRead(statusLed));  // Alterna o estado do LED a cada segundo
  }
}

///// FUNÇÕES DE CONEXÃO /////

void connectWiFi() {
  Serial.print("Conectando ao WiFi ");
  Serial.print(ssid);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);  // Aguarda meio segundo entre tentativas de conexão
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
    wifiRetries = 0;
    digitalWrite(statusLed, HIGH); // LED ligado indicando que a conexão WiFi foi bem-sucedida
  } else {
    Serial.println("\nFalha na conexão WiFi");
    digitalWrite(statusLed, LOW);  // LED desligado em caso de falha na conexão
  }
}

void handleWiFiDisconnection() {
  wifiRetries++;  // Incrementa o contador de tentativas de reconexão
  Serial.print("WiFi desconectado. Tentativa ");
  Serial.println(wifiRetries);

  if (wifiRetries > 10) {
    Serial.println("Reiniciando ESP...");
    ESP.restart();  // Reinicia o dispositivo caso falhe mais de 10 vezes ao tentar reconectar
  }

  WiFi.disconnect();  // Desconecta do WiFi e tenta reconectar
  delay(1000);        // Aguarda um segundo antes de tentar novamente
  connectWiFi();      // Tenta reconectar ao WiFi
}

void setupNTP() {
  timeClient.begin();  // Inicializa o cliente NTP
  Serial.print("Sincronizando horário NTP...");

  int attempts = 0;
  while (!timeClient.update() && attempts < 10) {  // Tenta sincronizar até 10 vezes
    delay(1000);  // Aguarda um segundo entre tentativas
    Serial.print(".");
    attempts++;
  }

  if (attempts < 10) {
    Serial.println(" OK!");
    Serial.println("Horário atual: " + timeClient.getFormattedTime());
  } else {
    Serial.println(" Falha na sincronização!");
  }
}

///// FUNÇÕES DE CONEXÃO COM O SERVIDOR  /////

// verifica a agenda
void checkSchedules() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, scheduleUrl);  // Inicia a requisição ao servidor de agendamentos
  http.setTimeout(10000);  // Timeout de 10 segundos para a requisição

  int httpCode = http.GET();  // Realiza a requisição GET para obter os agendamentos

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();  // Obtém a resposta do servidor
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);  // Deserializa o JSON recebido

    bool shouldActivate = doc["should_activate"];  // Verifica se a sirene deve ser ativada
    bool isScheduled = doc["is_scheduled"];      // Verifica se o comando foi agendado

    if (shouldActivate && !sirenActive) {
      String activationSource = isScheduled ? "agendamento" : "servidor";
      activateSiren(activationSource);  // Ativa a sirene se o comando for "ativar"
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
// verifica se ha comando manual
void checkManualCommands() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, commandUrl);  // Inicia a requisição ao servidor de comandos manuais
  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();  // Obtém a resposta do servidor
    DynamicJsonDocument doc(256);
    deserializeJson(doc, payload);  // Deserializa o JSON recebido

    // Verifica se existe comando e se é para ligar
    if (doc.containsKey("command") && doc["command"] == "ligar") {
      // Usa valor padrão se source não existir ou for null
      const char* source = doc["source"] | "manual";

      // Verifica se temos um ID válido
      if (doc.containsKey("id")) {
        String commandId = doc["id"];
        if (commandId != lastCommandId) {
          lastCommandId = commandId;
          activateSiren(String("manual (") + source + ")");
          confirmCommandExecution();
        }
      }
    }
  }
  http.end();
}
// confirma a execução do comando
void confirmCommandExecution() {
  WiFiClient client;
  HTTPClient http;

  http.begin(client, confirmUrl);  // URL para confirmar a execução do comando
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST("{}");  // Envia confirmação de que o comando foi executado

  if (httpCode == HTTP_CODE_OK) {
    Serial.println("Comando manual confirmado no servidor");
  } else {
    Serial.print("Erro ao confirmar comando: ");
    Serial.println(httpCode);
  }

  http.end();
}

///// CONTROLE DA SIRENE /////

// ativa sirene
void activateSiren(String source) {
  digitalWrite(sirenPin, LOW);  // Ativa a sirene
  sirenActive = true;
  sirenStartTime = millis();    // Marca o tempo de ativação

  Serial.print("Sirene ATIVADA por ");
  Serial.print(source);
  Serial.print(" às ");
  Serial.println(timeClient.getFormattedTime());

  // LED fica fixo ligado durante ativação
  digitalWrite(statusLed, HIGH);
}
// desativa a sirene
void deactivateSiren(String reason) {
  digitalWrite(sirenPin, HIGH);  // Desativa a sirene
  sirenActive = false;

  Serial.print("Sirene DESATIVADA (");
  Serial.print(reason);
  Serial.print(") às ");
  Serial.println(timeClient.getFormattedTime());

  // Retorna ao estado normal do LED
  digitalWrite(statusLed, LOW);
}

///// FUNÇÕES AUXILIAR DE DEBUG /////

void printDebugInfo() {
  Serial.println("\n=== DEBUG INFO ===");
  Serial.println("Horário atual: " + timeClient.getFormattedTime());
  Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado"));
  Serial.println("IP: " + WiFi.localIP().toString());
  Serial.println("Sirene: " + String(sirenActive ? "ATIVA" : "INATIVA"));
  Serial.println("Último comando ID: " + lastCommandId);
  Serial.println("==================\n");
}
