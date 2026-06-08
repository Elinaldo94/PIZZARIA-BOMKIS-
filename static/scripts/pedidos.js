const Pedidos = {
  async criarPedido(formData) {
    try {
      const response = await fetch("/vendas/api/pedido/novo/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...Auth.getAuthHeader(), // Usa o token do auth.js
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        alert("Sucesso! Pedido realizado. Previsão de retirada agendada.");
        window.location.reload(); // Recarrega para mostrar o novo card
      } else {
        alert(
          `Erro: ${data.erro || data.detail || "Falha ao processar pedido"}`,
        );
      }
    } catch (error) {
      console.error("Erro na requisição:", error);
    }
  },

  async cancelar(pedidoId) {
    if (!confirm("Deseja realmente cancelar este pedido?")) return;

    try {
      const response = await fetch(`/vendas/api/pedido/${pedidoId}/cancelar/`, {
        method: "POST",
        headers: Auth.getAuthHeader(),
      });

      if (response.ok) {
        alert("Pedido cancelado com sucesso.");
        window.location.reload();
      } else {
        const errorData = await response.json();
        alert(errorData.erro || "Não foi possível cancelar o pedido.");
      }
    } catch (error) {
      alert("Erro ao cancelar pedido.");
    }
  },

  async atualizarStatus(pedidoId) {
    try {
      const response = await fetch(`/vendas/api/pedido/${pedidoId}/status/`, {
        headers: Auth.getAuthHeader(),
      });

      if (response.ok) {
        const data = await response.json();
        this.renderizarStatusNoCard(pedidoId, data);
      }
    } catch (error) {
      console.error("Erro ao buscar status:", error);
    }
  },

  renderizarStatusNoCard(id, data) {
    const badge = document.querySelector(`#pedido-${id} .badge`);
    const progressBar =
      document.querySelector(`#pedido-${id} .progress-bar`) ||
      document.querySelector(`#pedido-${id} .progress > div`);

    if (badge && data.status_display) {
      badge.innerText = data.status_display.toUpperCase();
    }

    const progresso = {
      recebido: "20%",
      preparo: "50%",
      forno: "80%",
      no_forno: "80%",
      pronto: "100%",
    };

    if (progressBar) {
      progressBar.style.width = progresso[data.status_slug] || "100%";
    }
  },
};

document.addEventListener("DOMContentLoaded", () => {
  const formPedido = document.getElementById("form-novo-pedido");

  if (formPedido) {
    formPedido.addEventListener("submit", (e) => {
      e.preventDefault(); // Trava a submissão tradicional de página

      const pizzaSelect = document.querySelector('[name="pizza_id"]');
      const tamanhoRadio =
        document.querySelector('[name="tamanho"]:checked') ||
        document.querySelector('input[type="radio"]:checked');
      const pagamentoSelect = document.querySelector(
        '[name="metodo_pagamento"]',
      );
      const retiradaInput =
        document.querySelector('input[type="time"]') ||
        document.querySelector('[name="horario_retirada"]');

      if (!pizzaSelect || !tamanhoRadio || !pagamentoSelect || !retiradaInput) {
        console.error(
          "Erro de IHC: Alguns elementos do formulário HTML não foram encontrados pelo JS.",
        );
        alert(
          "Erro ao ler formulário. Por favor, selecione todas as opções (Sabor, Tamanho, Horário e Pagamento) antes de confirmar.",
        );
        return;
      }

      const formData = {
        pizza_id: pizzaSelect.value,
        tamanho: tamanhoRadio.value,
        metodo_pagamento: pagamentoSelect.value,
        horario_retirada: retiradaInput.value,
        ingredientes: [],
      };

      Pedidos.criarPedido(formData);
    });
  }

  document.body.addEventListener("click", (e) => {
    if (e.target && e.target.classList.contains("btn-outline-danger")) {
      const card = e.target.closest(".card");
      if (card && card.dataset.pedidoId) {
        e.preventDefault();
        Pedidos.cancelar(card.dataset.pedidoId);
      }
    }
  });

  const pedidosAtivos = document.querySelectorAll(
    '.card[data-status-ativo="true"]',
  );
  pedidosAtivos.forEach((card) => {
    const id = card.dataset.pedidoId;
    if (id) {
      setInterval(() => Pedidos.atualizarStatus(id), 30000);
    }
  });
});
