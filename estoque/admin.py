from django.contrib import admin
from .models import Fornecedor, Insumo, ReceitaPizza

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email') # Colunas que aparecem na lista
    search_fields = ('nome',) # Barra de busca por nome

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    # Mostra a quantidade e a unidade na tela principal
    list_display = ('nome', 'quantidade_atual', 'unidade_medida', 'nivel_critico', 'estoque_baixo')
    list_filter = ('unidade_medida', 'fornecedor') # Filtros laterais
    search_fields = ('nome',)

    # Função visual para alertar se o estoque está crítico
    @admin.display(boolean=True, description='Alerta Crítico?')
    def estoque_baixo(self, obj):
        return obj.quantidade_atual <= obj.nivel_critico

@admin.register(ReceitaPizza)
class ReceitaPizzaAdmin(admin.ModelAdmin):
    list_display = ('pizza', 'insumo', 'quantidade_usada')
    list_filter = ('pizza', 'insumo')
    search_fields = ('pizza__nome', 'insumo__nome') # Busca em campos relacionados