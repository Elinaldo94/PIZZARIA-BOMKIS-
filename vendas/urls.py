from django.urls import path
from . import views

urlpatterns = [
    # Telas HTML
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_cliente_view, name='home_cliente'),
    path('registrar/', views.registrar_view, name='registrar'),
    
    # API JSON
    path('api/pizzas/', views.api_pizzas, name='api_pizzas'), 
    path('api/pizzas/<int:pk>/', views.api_pizza_detalhe, name='api_pizzas_detail_update_delete'),
    path('api/registrar/', views.api_registrar_usuario, name='api_registrar_json'),
    path('api/login/', views.api_login, name='api_login_json'),

    path('pedido/cancelar/<int:pk>/', views.cancelar_pedido_view, name='cancelar_pedido'),
    path('pedido/editar/<int:pk>/', views.editar_pedido_view, name='editar_pedido'),
    path('pedido/novo/', views.novo_pedido_view, name='novo_pedido'),
]