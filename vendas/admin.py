from django.contrib import admin
from .models import Categoria, Pizza, Cliente, Ingrediente, Avaliacao

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco_m', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome',)

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'nivel_critico')
    # Destaca em vermelho se o estoque estiver baixo (opcional via CSS admin)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefone', 'data_cadastro')
    search_fields = ('usuario__username', 'telefone')

admin.site.register(Categoria)
admin.site.register(Avaliacao)
