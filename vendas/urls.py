from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # --- AUTENTICAÇÃO (SESSÃO DJANGO - TEMPLATES HTML) ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_cliente_view, name='home_cliente'),
    
    # ROTA ADICIONADA: Esta linha permite abrir o formulário vendas/registrar.html
    path('registrar/', views.registrar_view, name='registrar'), 

    # --- AUTENTICAÇÃO (JWT PARA API) ---
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/registrar/', views.RegistrarUsuarioAPI.as_view(), name='api_registrar'),
    path('api/perfil/', views.PerfilClienteAPIView.as_view(), name='api_perfil'),

    # --- CARDÁPIO ---
    path('api/pizzas/', views.PizzaListCreateAPIView.as_view(), name='api_pizzas'),
    path('api/pizzas/<int:pk>/', views.PizzaDetailAPIView.as_view(), name='api_pizza_detalhe'),
    path('api/cardapio/', views.CardapioAPIView.as_view(), name='api_cardapio'),
    path('cardapio/', views.cardapio_view, name='cardapio_visual'),

    # --- GESTÃO DE PEDIDOS ---
    path('api/pedido/novo/', views.NovoPedidoAPIView.as_view(), name='api_novo_pedido'),
    path('api/meus-pedidos/', views.MeusPedidosAPIView.as_view(), name='api_meus_pedidos'),
    path('api/pedido/<int:pk>/status/', views.StatusPedidoAPIView.as_view(), name='api_status_pedido'),
    path('api/pedido/<int:pk>/cancelar/', views.CancelarPedidoAPIView.as_view(), name='api_cancelar_pedido'),
    path('api/pedido/<int:pk>/editar/', views.EditarPedidoAPIView.as_view(), name='api_editar_pedido'),
    path('api/pedido/<int:pk>/status/', views.AtualizarStatusPedidoAPIView.as_view(), name='api_pedido_status'),

    # --- PAGAMENTO E FEEDBACK ---
    path('api/pedido/<int:pk>/pagar/', views.PagamentoPedidoAPIView.as_view(), name='api_pagar_pedido'),
    path('api/pedido/<int:pk>/avaliar/', views.AvaliarPedidoAPIView.as_view(), name='api_avaliar_pedido'),
]
