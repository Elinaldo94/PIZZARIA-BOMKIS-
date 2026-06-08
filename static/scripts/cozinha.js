/**
 * cozinha.js - Controle de Fila e Monitoramento de Fornos (Pizzaria Bomkisó)
 */

const Cozinha = {
  // 1. Dispara a fornada agrupando pizzas na API
  async iniciarFornada() {
    try {
      const response = await fetch("/producao/api/fornada/iniciar/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...Auth.getAuthHeader(), // CORRIGIDO: Mesclagem correta do Token Bearer sem apagar o Content-Type
        },
      });

      if (response.ok) {
        const data = await response.json();
        alert(
          `Sucesso! Fornada #${data.fornada_id} iniciada com ${data.pizzas_no_forno} pizzas.`,
        );
        window.location.reload(); // Recarrega para atualizar a fila e os timers
      } else {
        const errorData = await response.json();
        alert(errorData.erro || errorData.detail || "Erro ao iniciar fornada.");
      }
    } catch (error) {
      console.error("Erro na cozinha:", error);
    }
  },

  // 2. Controla os cronômetros regressivos do forno na tela (UX/IHC)
  iniciarTimers() {
    const timers = document.querySelectorAll(".timer");

    timers.forEach((timer) => {
      const conclusaoStr = timer.dataset.conclusao;
      const metaTime = new Date(conclusaoStr).getTime();

      const intervalo = setInterval(() => {
        const agora = new Date().getTime();
        const diff = metaTime - agora;

        if (diff <= 0) {
          clearInterval(intervalo);
          timer.innerText = "RETIRAR AGORA! 🍕";
          timer.classList.remove("bg-dark");
          timer.classList.add(
            "bg-danger",
            "animate__animated",
            "animate__pulse",
            "animate__infinite",
          );
          Cozinha.notificarCozinha(); // Alerta sonoro/visual
        } else {
          const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          const segundos = Math.floor((diff % (1000 * 60)) / 1000);
          timer.innerText = `⏳ ${minutos}m ${segundos}s`;
        }
      }, 1000);
    });
  },

  // 3. Notificação IHC para o pizzaiolo não queimar os insumos
  notificarCozinha() {
    console.log("ALERTA: Fornada pronta para retirada!");
  },
};

// --- INICIALIZAÇÃO DE EVENTOS ---
// --- NOVO ORQUESTRADOR DE EVENTOS NO COZINHA.JS ---
document.addEventListener("DOMContentLoaded", () => {
  const btnFornada = document.getElementById("btn-iniciar-fornada");
  if (btnFornada) {
    btnFornada.addEventListener("click", () => Cozinha.iniciarFornada());
  }

  // Captura cliques nos botões de avançar status (Pronto / Concluído) via API JWT
  document.body.addEventListener("click", async (e) => {
    if (e.target && e.target.classList.contains("btn-status")) {
      e.preventDefault();
      const pedidoId = e.target.dataset.id;
      const novoStatus = e.target.dataset.status;

      if (
        !confirm(
          `Deseja alterar o status do Pedido #${pedidoId} para ${novoStatus.toUpperCase()}?`,
        )
      )
        return;

      try {
        // Envia a requisição direto para a sua API padrão de atualização de status do pedido
        const response = await fetch(`/vendas/api/pedido/${pedidoId}/status/`, {
          method: "POST", // ou PUT/PATCH conforme mapeado na sua view
          headers: {
            "Content-Type": "application/json",
            ...Auth.getAuthHeader(), // Envia o token JWT do admin promovido
          },
          body: JSON.stringify({ status: novoStatus }),
        });

        if (response.ok) {
          alert("Status atualizado com sucesso no banco de dados!");
          window.location.reload(); // Recarrega a tela para redesenhar os botões
        } else {
          alert("Erro operacional ao atualizar o status do pedido.");
        }
      } catch (err) {
        console.error("Erro de conexão na API de produção:", err);
      }
    }
  });

  // Ativa os cronômetros das fornadas
  if (typeof Cozinha.iniciarTimers === "function") Cozinha.iniciarTimers();
});
