from django.urls import path
from . import views

urlpatterns = [
    # Operacional
    path('novo-pedido/', views.api_criar_pedido, name='api_criar_pedido'),
    path('meus-pedidos/', views.api_listar_meus_pedidos, name='api_listar_pedidos'),
]