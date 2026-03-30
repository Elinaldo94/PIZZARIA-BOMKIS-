from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.painel_preparo, name='painel_preparo'),
    path('api/critico/', views.api_estoque_critico, name='api_estoque_critico'),
]