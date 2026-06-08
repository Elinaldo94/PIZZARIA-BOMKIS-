const Estoque = {
  // 1. Envia a compra para a API injetando o Token Bearer JWT de forma segura
  async registrarEntrada(dadosCompra) {
    try {
      const response = await fetch("/estoque/api/comprar/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...Auth.getAuthHeader(), // Elimina o erro 401 do console
        },
        body: JSON.stringify(dadosCompra),
      });

      if (response.ok) {
        alert(
          "Sucesso! Compra registrada e estoque atualizado automaticamente.",
        );
        window.location.reload();
      } else {
        const errorData = await response.json();
        alert(
          errorData.erro || errorData.detail || "Erro ao registrar compra.",
        );
      }
    } catch (error) {
      console.error("Erro na requisição de estoque:", error);
    }
  },
};

// --- ORQUESTRADOR DE EVENTOS DA INTERFACE ---
document.addEventListener("DOMContentLoaded", () => {
  const btnRegistrarCompra = document.getElementById("btn-abrir-formulario");
  const btnCancelar = document.getElementById("btn-cancelar-compra");
  const painelFormulario = document.getElementById("painel-formulario-compra");
  const formCompra = document.getElementById("form-registrar-compra");

  // A. Ação do Botão REGISTRAR COMPRA (Abre o painel vermelho)
  if (btnRegistrarCompra && painelFormulario) {
    btnRegistrarCompra.addEventListener("click", (e) => {
      e.preventDefault();
      painelFormulario.style.display = "block"; // Faz o painel aparecer
    });
  }

  // B. Ação do Botão CANCELAR (Fecha o painel vermelho)
  if (btnCancelar && painelFormulario) {
    btnCancelar.addEventListener("click", (e) => {
      e.preventDefault();
      painelFormulario.style.display = "none"; // Esconde o painel
    });
  }

  // C. Interceptação do Envio (Botão CONFIRMAR ENTRADA)
  if (formCompra) {
    formCompra.addEventListener("submit", (e) => {
      e.preventDefault(); // Impede o navegador de recarregar a página com erro

      const insumoSelect = document.getElementById("insumo_id");
      const quantidadeInput = document.getElementById("quantidade_comprada");

      if (!insumoSelect || !quantidadeInput || !insumoSelect.value) {
        alert("Por favor, selecione um insumo e informe a quantidade.");
        return;
      }

      const dadosCompra = {
        insumo_id: parseInt(insumoSelect.value),
        quantidade: parseFloat(quantidadeInput.value.replace(",", ".")),
      };

      console.log("Enviando entrada de insumo via API:", dadosCompra);
      Estoque.registrarEntrada(dadosCompra);
    });
  }
});
