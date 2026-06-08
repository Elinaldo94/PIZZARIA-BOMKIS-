from django.contrib import admin
from .models import Fornecedor, Insumo, ReceitaPizza, RegistroCompra

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    # Colunas úteis para o dia a dia da pizzaria
    list_display = ('nome', 'quantidade_atual', 'unidade_medida', 'nivel_critico', 'estoque_critico')
    list_filter = ('unidade_medida', 'fornecedor')
    search_fields = ('nome',)

    # Função visual para o Admin: Mostra uma "luz" vermelha/verde para o estoque
    @admin.display(boolean=True, description='Status Crítico')
    def estoque_critico(self, obj):
        return obj.quantidade_atual <= obj.nivel_critico

@admin.register(RegistroCompra)
class RegistroCompraAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'quantidade', 'valor_pago', 'data')
    list_filter = ('data', 'insumo')
    date_hierarchy = 'data' # Adiciona uma barra de navegação por data no topo

@admin.register(ReceitaPizza)
class ReceitaPizzaAdmin(admin.ModelAdmin):
    list_display = ('pizza', 'insumo', 'quantidade_usada')
    search_fields = ('pizza__nome', 'insumo__nome')

admin.site.register(Fornecedor)
