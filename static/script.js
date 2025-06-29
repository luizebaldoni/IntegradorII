// Estrutura para armazenar os horários
let horarios = {};
 // Função para carregar os agendamentos via API
    async function carregarAgendamentos() {
        try {
            const response = await fetch('');  // Endereço do endpoint da view HomeView
            const data = await response.json();

            const horariosContainer = document.getElementById('horarios-container');
            const horariosList = document.createElement('ul');
            horariosContainer.appendChild(horariosList);

            data.alarms.forEach(alarm => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `<strong>${alarm.event_type}</strong>: ${alarm.time} (${alarm.start_date} → ${alarm.end_date})`;
                horariosList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Erro ao carregar os agendamentos:', error);
        }
    }

    // Chama a função para carregar os agendamentos quando a página for carregada
    document.addEventListener('DOMContentLoaded', carregarAgendamentos);
// Carregar horários salvos
function carregarHorarios() {
    const horariosSalvos = localStorage.getItem('horariosEscola');
    if (horariosSalvos) {
        horarios = JSON.parse(horariosSalvos);
    }
    atualizarInterface();
}

// Salvar horários no localStorage
function salvarHorarios() {
    localStorage.setItem('horariosEscola', JSON.stringify(horarios));
}

// Adicionar novo horário
function adicionarHorario() {
    const dia = document.getElementById('dia').value;
    const horario = document.getElementById('horario').value;
    const descricao = document.getElementById('descricao').value;

    if (!horario || !descricao) {
        mostrarNotificacao('Por favor, preencha todos os campos!', 'erro');
        return;
    }

    // Validar o formato do horário
    if (!validarHorario(horario)) {
        mostrarNotificacao('Horário inválido! Use o formato HH:mm.', 'erro');
        return;
    }

    // Inicializar array do dia se não existir
    if (!horarios[dia]) {
        horarios[dia] = [];
    }

    // Verificar se já existe esse horário no dia
    const jaExiste = horarios[dia].some(h => h.horario === horario);
    if (jaExiste) {
        mostrarNotificacao('Já existe um horário cadastrado para esse mesmo horário!', 'erro');
        return;
    }

    // Adicionar novo horário
    horarios[dia].push({
        horario: horario,
        descricao: descricao
    });

    // Ordenar horários por ordem crescente
    horarios[dia].sort((a, b) => a.horario.localeCompare(b.horario));

    salvarHorarios();
    atualizarInterface();
    mostrarNotificacao('Horário adicionado com sucesso!', 'sucesso');

    // Limpar formulário
    document.getElementById('horario').value = '';
    document.getElementById('descricao').value = '';
}

// Remover horário
function removerHorario(dia, index) {
    if (confirm('Tem certeza que deseja remover este horário?')) {
        horarios[dia].splice(index, 1);
        if (horarios[dia].length === 0) {
            delete horarios[dia];
        }
        salvarHorarios();
        atualizarInterface();
    }
}

// Atualizar a interface com os horários salvos
function atualizarInterface() {
    const container = document.getElementById('horarios-container');
    container.innerHTML = '';

    const diasSemana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'];
    const nomesDias = { // "Traduz" os nomes curtos para os completos
        'segunda': 'Segunda-feira',
        'terca': 'Terça-feira',
        'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira',
        'sexta': 'Sexta-feira',
        'sabado': 'Sábado',
        'domingo': 'Domingo'
    };

    diasSemana.forEach(dia => { // Para cada dia da semana, criar um card
        const diaCard = document.createElement('div');
        diaCard.className = 'dia-card';

        let horariosHtml = '';
        if (horarios[dia] && horarios[dia].length > 0) {
            // Se tiver horarios para o dia, mostra o horário, descrição e botão de remover
            horarios[dia].forEach((horario, index) => {
                horariosHtml += `
                    <div class="horario-item">
                        <div>
                            <div class="horario-time">${horario.horario}</div>
                            <div class="horario-desc">${horario.descricao}</div>
                        </div>
                        <button class="delete-btn" onclick="removerHorario('${dia}', ${index})">✕</button>
                    </div>
                `;
            });
        } else {
            // Se não tiver horários para o dia, mostra mensagem de "nenhum horário cadastrado"
            horariosHtml = '<p style="color: #7f8c8d; font-style: italic;">Nenhum horário cadastrado</p>';
        }

        // Montando o card e adicionando ao HTML
        diaCard.innerHTML = `
            <h3>${nomesDias[dia]}</h3>
            ${horariosHtml}
        `;
        container.appendChild(diaCard);
    });
}

// Função para mostrar notificações de sucesso ou erro
function mostrarNotificacao(mensagem, tipo) {
    const notificacao = document.createElement('div');
    notificacao.classList.add('notificacao', tipo);
    notificacao.textContent = mensagem;
    document.body.appendChild(notificacao);

    setTimeout(() => {
        notificacao.remove();
    }, 3000); // Remove a notificação após 3 segundos
}

// Função para validar o formato do horário (HH:mm)
function validarHorario(horario) {
    const regex = /^([01]?[0-9]|2[0-3]):([0-5][0-9])$/;
    return regex.test(horario);
}

// Inicializar o sistema
document.addEventListener('DOMContentLoaded', function() {
    carregarHorarios(); // Carrega os horários salvos ao carregar a página
});
