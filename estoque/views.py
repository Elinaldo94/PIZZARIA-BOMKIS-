from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F
from .models import Insumo

def painel_preparo(request):
    """Tela HTML: Lista todos os insumos e destaca os que estão baixos"""
    insumos = Insumo.objects.all().order_by('quantidade_atual')
    return render(request, 'estoque/painel.html', {'insumos': insumos})

def api_estoque_critico(request):
    """API JSON: Retorna apenas os itens abaixo do nível crítico para alertas"""
    criticos = Insumo.objects.filter(
        quantidade_atual__lte=F('nivel_critico')
    ).values('nome', 'quantidade_atual', 'unidade_medida', 'nivel_critico')
    
    return JsonResponse(list(criticos), safe=False)