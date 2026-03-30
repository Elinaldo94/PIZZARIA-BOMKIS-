from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Painel Administrativo do Django
    path('admin/', admin.site.urls),

    # App Vendas: Gerencia Login, Registro e Cardápio
    path('vendas/', include('vendas.urls')),

    # App Produção: Gerencia Pedidos e Fornadas
    path('producao/', include('producao.urls')),

    # App Estoque: Gerencia Insumos e Fornecedores
    path('estoque/', include('estoque.urls')),

    # App Gestão: Dashboard e Relatórios Estratégicos
    path('gestao/', include('gestao.urls')),
    
]