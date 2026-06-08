from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required  # Adicionado para segurança
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count

from producao.models import Pedido
from vendas.models import Pizza
from .models import EscalaTrabalho, Funcionario

# --- VIEWS PARA O NAVEGADOR (HTML) ---
@login_required
def dashboard_gerencial(request):
    """Renderiza a página HTML do Dashboard calculando o faturamento real"""
    from vendas.models import ItemPedido
    
    # Busca todos os itens de pedidos finalizados com sucesso
    itens_concluidos = ItemPedido.objects.filter(pedido__status='concluido').select_related('pizza')
    
    # Calcula o faturamento real com base no preço de cada tamanho vendido
    faturamento = 0
    for item in itens_concluidos:
        if item.tamanho == 'P':
            faturamento += item.pizza.preco_p
        elif item.tamanho == 'M':
            faturamento += item.pizza.preco_m
        else:
            faturamento += item.pizza.preco_g

    # 2. Lucro Líquido Projetado (40% do faturamento real)
    lucro_projetado = float(faturamento) * 0.40
    
    # 3. Indicadores de Volume
    total_pedidos = Pedido.objects.count()
    pedidos_telefone = Pedido.objects.filter(prioridade=True).count()
    
    # 4. Operação em Tempo Real (Resumo por Status)
    resumo_status = Pedido.objects.values('status').annotate(total=Count('status'))
    
    # 5. Ranking das 5 mais pedidas (Top 5)
    pizzas_populares = Pizza.objects.annotate(
        vendas=Count('itempedido') # Ajustado seletor reverso correto
    ).order_by('-vendas')[:5]

    context = {
        'faturamento': faturamento,
        'lucro_projetado': lucro_projetado,
        'total_pedidos': total_pedidos,
        'pedidos_telefone': pedidos_telefone,
        'resumo_status': resumo_status,
        'pizzas_populares': pizzas_populares,
    }
    
    return render(request, 'gestao/dashboard.html', context)


@login_required
def gestao_equipe_view(request):
    """Renderiza a página HTML de gestão de equipe"""
    hoje = timezone.now().date()
    escala = EscalaTrabalho.objects.filter(data=hoje).prefetch_related('funcionarios__usuario').first()
    
    return render(request, 'gestao/equipe.html', {
        'escala': escala, 
        'hoje': hoje
    })


# --- VIEWS DE API (JSON PARA O FUTURO/APP) ---

class DashboardBIAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        faturamento = Pedido.objects.filter(status='concluido').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        lucro_projetado = float(faturamento) * 0.40 
        ranking = Pizza.objects.annotate(vendas=Count('pedido')).order_by('-vendas')[:5].values('nome', 'vendas')

        return Response({
            "operacional": {
                "total_pedidos": Pedido.objects.count(),
                "pedidos_hoje": Pedido.objects.filter(horario_pedido__date=timezone.now().date()).count(),
            },
            "financeiro": {
                "faturamento_bruto": float(faturamento),
                "lucro_estimado": lucro_projetado,
            },
            "produtos": list(ranking)
        })

class GestaoEscalaAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, data_escala):
        escala = get_object_or_404(EscalaTrabalho, data=data_escala)
        funcionario_id = request.data.get('substituir_id')
        novo_funcionario_id = request.data.get('novo_id')
        
        if funcionario_id and novo_funcionario_id:
            escala.funcionarios.remove(funcionario_id)
            escala.funcionarios.add(novo_funcionario_id)
            escala.save()
            return Response({"msg": "Escala reorganizada!"})
        
        return Response({"erro": "Dados insuficientes"}, status=status.HTTP_400_BAD_REQUEST)
