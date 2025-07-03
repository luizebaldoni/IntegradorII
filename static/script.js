/***********************************************
 * Descrição:
 *  Este script implementa a lógica para envio de uma requisição POST
 *  ao servidor com a finalidade de ativar uma sirene remotamente
 *  por meio da interface web. Inclui feedback visual, notificações e
 *  controle de estado do botão.
 ************************************************/

/**
 * Ativa a sirene via requisição POST para a rota Django definida.
 * Fornece feedback visual ao usuário (spinner, botão desabilitado e texto).
 */

async function ativarSirene() {
  const btn = document.getElementById('sirenButton');
  const btnText = document.getElementById('sirenButtonText');
  const spinner = document.getElementById('sirenSpinner');

  // Inicia estado de carregamento
  btn.disabled = true;
  btnText.textContent = "Enviando...";
  spinner.classList.remove('d-none');

  try {
    const response = await fetch("{% url 'app:ativar-campainha' %}", {
      method: 'POST',
      headers: {
        'X-CSRFToken': '{{ csrf_token }}',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        duration: 5,             // Duração da sirene em segundos
        source: 'web_interface'   // Fonte de acionamento
      })
    });

    if (!response.ok) throw new Error('Erro na resposta do servidor');

    const data = await response.json();

    // Feedback de sucesso
    mostrarNotificacao('Sirene ativada com sucesso!', 'sucesso');
    btnText.textContent = "Sirene acionada!";

    // Reset do botão após 3 segundos
    setTimeout(() => {
      btnText.textContent = "Tocar Sirene";
      spinner.classList.add('d-none');
      btn.disabled = false;
    }, 3000);
  } catch (error) {
    console.error('Erro:', error);

    // Feedback de erro
    btnText.textContent = "Erro! Tentar novamente";
    spinner.classList.add('d-none');
    btn.disabled = false;
    mostrarNotificacao('Erro ao ativar sirene', 'erro');
  }
}

/**
 * Exibe uma notificação visual no canto inferior com fade temporizado.
 * @param {string} mensagem - Texto da notificação.
 * @param {string} tipo - 'sucesso' ou 'erro', define o ícone e estilo.
 */
function mostrarNotificacao(mensagem, tipo) {
  const notificacao = document.createElement('div');
  notificacao.classList.add('notificacao', tipo);

  // Ícone condicional baseado no tipo
  const icon = tipo === 'sucesso' ? '✓' : '✕';
  notificacao.innerHTML = `<span class="notificacao-icon">${icon}</span> ${mensagem}`;

  document.body.appendChild(notificacao);

  // Animação de entrada
  setTimeout(() => {
    notificacao.classList.add('show');
  }, 10);

  // Remoção automática com fade após 3 segundos
  setTimeout(() => {
    notificacao.classList.remove('show');
    setTimeout(() => {
      notificacao.remove();
    }, 300);
  }, 3000);
}

/**
 * Inicializa ícones Feather e tooltips Bootstrap após o carregamento do DOM.
 */
document.addEventListener('DOMContentLoaded', function() {
  feather.replace(); // Substitui ícones <i> com SVGs do Feather

  // Inicializa tooltips com Bootstrap 5
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});
// Ativar item do menu correspondente à página atual
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar__link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

function confirmarExclusao(url) {
    if (confirm('Tem certeza que deseja excluir este agendamento?')) {
        window.location.href = url;
    }
}

// Atualizar os links de exclusão para usar esta função
document.querySelectorAll('.btn-excluir').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        confirmarExclusao(this.href);
    });
});