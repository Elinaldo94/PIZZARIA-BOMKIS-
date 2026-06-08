/**
 * auth.js - Gestão de Autenticação JWT (Pizzaria Bomkisó)
 */
const API_URL = "/vendas/api/login/";

const Auth = {
  // 1. Realiza a chamada assíncrona para a API e armazena os Tokens
  async login(username, password) {
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        throw new Error("Usuário ou senha inválidos");
      }
      const data = await response.json();

      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("username", username);

      window.location.href = "/vendas/home/";
    } catch (error) {
      alert("Erro no Login: " + error.message);
    }
  },

  // 2. FORNECE O CABEÇALHO EXIGIDO PELO PEDIDOS.JS (CORREÇÃO DO ERRO DO PRINT)
  getAuthHeader() {
    const token = localStorage.getItem("access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  // 3. Limpa os rastros de autenticação e desloga completamente
  logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/vendas/login/";
  },
};

// --- ORQUESTRADOR DE INTERFACE E ACESSO ---
document.addEventListener("DOMContentLoaded", () => {
  const localizacao = window.location.pathname;

  // Barreira de Proteção Frontend
  if (
    localizacao !== "/vendas/login/" &&
    localizacao !== "/vendas/registrar/"
  ) {
    if (!localStorage.getItem("access_token")) {
      console.warn("Acesso negado. Redirecionando...");
      window.location.href = "/vendas/login/";
      return;
    }
  }

  // Interceptador do Formulário de Login
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const user = document.getElementById("username").value;
      const pass = document.getElementById("password").value;
      Auth.login(user, pass);
    });
  }

  // Listener do Botão Sair
  const btnLogout = document.getElementById("btn-logout");
  if (btnLogout) {
    btnLogout.addEventListener("click", (e) => {
      e.preventDefault();
      if (confirm("Deseja realmente sair do sistema?")) {
        Auth.logout();
      }
    });
  }

  // Montagem Dinâmica da Navbar com Token Ativo
  if (localStorage.getItem("access_token")) {
    if (document.getElementById("menu-operacional"))
      document.getElementById("menu-operacional").style.display = "block";
    if (document.getElementById("auth-logged-in"))
      document.getElementById("auth-logged-in").style.display = "block";
    if (document.getElementById("nav-username"))
      document.getElementById("nav-username").innerText =
        localStorage.getItem("username");
  }
});
