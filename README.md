# 📣 School Buzzer

**Campainha automática inteligente para escolas — programável via Web, com atualização OTA e controle em tempo real.**

![school-buzzer-banner](https://via.placeholder.com/800x200?text=School+Buzzer)

---

## 🚀 Sobre o Projeto

O **School Buzzer** é um sistema eletrônico inteligente desenvolvido para automatizar os toques de campainha em escolas, trazendo modernização, pontualidade e facilidade de controle por meio de uma interface web intuitiva. Ideal para instituições que buscam reduzir a dependência de toques manuais e manter rotinas organizadas com precisão.

---

## ⚙️ Funcionalidades

- ⏰ **Programação de Horários** via painel Web
- 🌐 **Conectividade Wi-Fi** com ESP32
- 🔄 **Atualização OTA (Over-The-Air)** do firmware
- 🔊 **Ativação automática** de buzzer ou sirene conforme horários definidos
- 📱 **Painel de controle responsivo** (mobile e desktop)
- 📋 **Log de eventos**: registro de toques emitidos
- 🔘 **Modo manual** para toques instantâneos
- 📲 **Integração opcional com WhatsApp/App** para notificações de horários especiais

---

## 🧠 Tecnologias Utilizadas

### 📡 Hardware
- [x] ESP32 com suporte OTA
- [x] Buzzer 5V ou Sirene 12V
- [x] Módulo Relé (caso sirene seja usada)
- [x] Alimentação via fonte ou baterias 18650
- [x] Protoboard / Fenolite / Jumpers

### 💻 Software
- 🔧 **Firmware em C++ (Arduino IDE)**
- 🌐 **Painel Web:** HTML, CSS, JavaScript
- 🔙 **Back-End:** Node.js ou Python (Flask)
- 🗃️ **Banco de Dados:** Firebase / MySQL
- 📶 **Comunicação:** HTTP/WebSocket

---

## 🛠️ Como Funciona

1. A diretoria acessa o painel web e cadastra os horários de toque.
2. O servidor salva as configurações no banco de dados.
3. O ESP32 sincroniza os dados via Wi-Fi.
4. A cada ciclo de tempo, o microcontrolador verifica os horários e aciona a campainha automaticamente.
5. Atualizações no sistema podem ser feitas remotamente via OTA.

---

## 🧰 Lista de Materiais

| Item | Descrição | Qtde |
|------|-----------|------|
| ESP32 | Microcontrolador Wi-Fi | 1 |
| Buzzer 5V ou Sirene 12V | Emissor de som | 1 |
| Módulo Relé | Acionamento da sirene | 1 |
| Protoboard / Fenolite | Montagem | 1 |
| Fonte 5V ou Bateria 18650 | Alimentação | 1 |
| Módulo TP4056 + Step-Up | Recarga e elevação de tensão | 1 |
| Fios, conectores, jumpers | Montagem elétrica | diversos |

---

## Progresso do Software

- [x] Esboço da idéia da aplicação
- [x] Definição da linguagem e framework
- [ ] Criação do projeto
- [ ] Definir back-end e front-end
- [ ] Criação da database
- [ ] Receber informações do hardware e salvar na database
- [ ] Criação da pagina inicial
- [ ] Criar sistema de definição de horários e dias (salvar na database)
- [ ] Criar função de adicionar horários e dias para sirene tocar
- [ ] Criar função de remover horarios e dias para sirene tocar
- [ ] Criar função de ativar atraves de botao a sirene instantaneamente
- [ ] Mostrar na tela quais dias e horários estao definidos
- [ ] Definir testes
  
## Progresso do Hardware
- [x] Definir microcontrolador a ser utilizado
- [ ] Adquirir materiais
- [ ] Criar circuito
- [ ] Incluir sistema OTA
- [ ] Enviar dados/status da sirene para o servidor
- [ ] Receber informações do servidor
- [ ] Criar case


---

## 👨‍🔬 Desenvolvido por

**Disciplina de Projeto Integrador II — Engenharia da Computação UFSM**

Equipe de Software:
- Eduardo Schlesner
- Leonardo Moscheta
- Higor Brum

Equipe de Hardware:
- Matheus Miranda
- Vinicios Ramos
- Gabriela Belardorni
- Maria Eduarda Haidar

Equipe de Integração:
- Luize Baldoni

---

## 📄 Licença



---

## 📬 Contato


---

