from django.shortcuts import render  # IMPORTAÇÃO NECESSÁRIA
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Case, When, Value, IntegerField
from .models import Pedido, Fornada
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required



class PainelProducaoAPIView(APIView):
    """
    API JSON: Lista a fila organizada por prioridade (Telefone primeiro).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        fila = Pedido.objects.filter(status='recebido').order_by(
            Case(
                When(prioridade=True, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
            'horario_pedido'
        )
        
        # Otimizado para retornar a contagem real de pizzas na fila
        dados = [{
            "id": p.id, 
            "prioridade": p.prioridade, 
            "qtd_pizzas": p.pizzas.count(),
            "cliente": p.cliente.usuario.username if p.cliente else p.cliente_nome_avulso
        } for p in fila]
        
        return Response(dados)


class GerarFornadaAPIView(APIView):
    # Garante que apenas usuários com status de staff/admin possam iniciar o forno
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            # Coleta até 9 pizzas que estão aguardando preparo na fila
            pedidos_fila = Pedido.objects.filter(status='recebido').order_by('prioridade', 'horario_pedido')[:9]
            
            if not pedidos_fila.exists():
                return Response({"erro": "Nenhum pedido na fila aguardando preparo."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cria a fornada com previsão de término para daqui a 15 minutos
            fornada = Fornada.objects.create(
                previsao_conclusao=timezone.now() + timedelta(minutes=15)
            )
            
            # Move os pedidos da fila para dentro do forno e atualiza o status
            quantidade_pizzas = 0
            for pedido in pedidos_fila:
                fornada.pedidos.add(pedido)
                pedido.status = 'forno'  # Altera o status para rastreio
                pedido.save()
                quantidade_pizzas += 1
                
            fornada.save()

            # Retorna o JSON exato esperado pelo cozinha.js
            return Response({
                "fornada_id": fornada.id,
                "pizzas_no_forno": quantidade_pizzas,
                "msg": "Fornada iniciada com sucesso!"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Evita o erro 500 genérico e te diz exatamente no terminal o que quebrou
            return Response({"erro": f"Erro interno no servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- VIEW DE TEMPLATE (HTML) ---

def painel_cozinha_view(request):
    """Renderiza a página HTML da cozinha com pedidos e fornadas ativas."""
    # Filtra pedidos que ainda não entraram no forno
    pedidos = Pedido.objects.filter(status__in=['recebido', 'preparo']).order_by('-prioridade', 'horario_pedido')
    
    # Filtra fornadas que ainda estão assando
    fornadas = Fornada.objects.filter(concluida=False).order_by('inicio_forno')
    
    return render(request, 'producao/painel.html', {
        'pedidos_aguardando': pedidos,
        'fornadas_ativas': fornadas
    })


@login_required
def painel_producao_view(request):
    """
    CORRIGIDO: Varrer todas as três etapas ativas da esteira (recebido, forno e pronto)
    para permitir que o pizzaiolo controle o andamento das pizzas na tela.
    """
    # Buscamos os pedidos em qualquer uma das três fases de produção ativas
    pedidos_ativos = Pedido.objects.filter(
        status__in=['recebido', 'forno', 'pronto']
    ).order_by('prioridade', 'horario_pedido')
    
    return render(request, 'producao/painel.html', {
        'pedidos_aguardando': pedidos_ativos # Alinhado com a variável do seu loop {% for %}
    })
