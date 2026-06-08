from django.contrib import admin
from .models import Pedido, Fornada

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Cores e ícones para prioridade e status
    list_display = ('id', 'exibir_identificacao', 'status', 'prioridade', 'horario_pedido', 'pago')
    list_filter = ('status', 'prioridade', 'origem')
    search_fields = ('cliente__usuario__username', 'cliente_nome_avulso')
    
    def exibir_identificacao(self, obj):
        return obj.cliente.usuario.username if obj.cliente else f"📞 {obj.cliente_nome_avulso}"
    exibir_identificacao.short_description = 'Cliente / Identificação'

@admin.register(Fornada)
class FornadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'inicio_forno', 'previsao_conclusao', 'concluida', 'qtd_pedidos')
    list_filter = ('concluida',)
    
    def qtd_pedidos(self, obj):
        return obj.pedidos.count()
    qtd_pedidos.short_description = 'Pizzas na Fornada'
