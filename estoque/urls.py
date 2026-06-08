from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.painel_preparo, name='painel_preparo'), 
    path('api/critico/', views.EstoqueCriticoAPIView.as_view(), name='api_estoque_critico'),
    path('api/comprar/', views.RegistrarCompraAPIView.as_view(), name='api_registrar_compra'),
]
