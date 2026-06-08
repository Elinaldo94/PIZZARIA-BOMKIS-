from django.urls import path
from . import views

urlpatterns = [
    # Mudei o nome da API para não dar conflito com a página HTML
    path('api/painel/', views.PainelProducaoAPIView.as_view(), name='api_painel_producao'),
    path('api/fornada/iniciar/', views.GerarFornadaAPIView.as_view(), name='iniciar_fornada'),
    
    # Esta é a página que o Pizzaiolo acessa no navegador
    path('painel/', views.painel_cozinha_view, name='painel_producao'),
]
