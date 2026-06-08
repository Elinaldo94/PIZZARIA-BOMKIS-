from django.contrib import admin
from .models import Funcionario, EscalaTrabalho

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'funcao', 'ativo')
    list_filter = ('funcao', 'ativo')

@admin.register(EscalaTrabalho)
class EscalaAdmin(admin.ModelAdmin):
    list_display = ('data', 'tipo_dia')
    filter_horizontal = ('funcionarios',) # Facilita selecionar múltiplos na escala
