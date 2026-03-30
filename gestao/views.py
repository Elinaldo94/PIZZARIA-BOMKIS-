from django.shortcuts import render
from django.db.models import Count
from producao.models import Pedido
from vendas.models import Pizza

def dashboard_gerencial(request):
    """Tela HTML: Painel de indicadores para a dona da pizzaria"""
    # 1. Total de pedidos realizados no sistema
    total_pedidos = Pedido.objects.count()
    
    # 2. Resumo de status (Quantos em preparo, quantos no forno, etc.)
    resumo_status = Pedido.objects.values('status').annotate(total=Count('status'))
    
    # 3. Ranking das 5 pizzas mais pedidas (Diferencial Estratégico)
    pizzas_populares = Pizza.objects.annotate(
        qtd_vendas=Count('pedido')
    ).order_by('-qtd_vendas')[:5]

    context = {
        'total_pedidos': total_pedidos,
        'resumo_status': resumo_status,
        'pizzas_populares': pizzas_populares,
    }
    return render(request, 'gestao/dashboard.html', context)