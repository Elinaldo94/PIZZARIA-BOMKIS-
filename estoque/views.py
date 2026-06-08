from django.shortcuts import render  # IMPORTAÇÃO NECESSÁRIA PARA O HTML
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import F 
from .models import Insumo, RegistroCompra
from .serializers import InsumoSerializer, RegistroCompraSerializer
from django.shortcuts import get_object_or_404

# --- VIEWS DE API (JSON) ---


class RegistrarCompraAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Captura as variações de chaves enviadas pelo frontend
        data = request.data
        insumo_id = data.get('insumo_id') or data.get('insumo')
        quantidade_str = data.get('quantidade') or data.get('quantidade_comprada')

        if not insumo_id or not quantidade_str:
            return Response({"erro": "Insumo ou quantidade não informados."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Busca o ingrediente no banco de dados
            insumo = get_object_or_404(Insumo, id=int(insumo_id))
            
            # Converte e soma o saldo atualizado
            quantidade_somar = float(quantidade_str)
            insumo.quantidade_atual = float(insumo.quantidade_atual) + quantidade_somar
            insumo.save()

            return Response({
                "status": "sucesso",
                "mensagem": "Estoque atualizado com sucesso!",
                "novo_saldo": insumo.quantidade_atual
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"erro": f"Erro interno ao salvar estoque: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class EstoqueCriticoAPIView(APIView):
    """Retorna via JSON itens com estoque baixo"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        insumos_baixos = Insumo.objects.filter(quantidade_atual__lte=F('nivel_critico'))
        serializer = InsumoSerializer(insumos_baixos, many=True)
        return Response({
            "total_criticos": insumos_baixos.count(),
            "itens": serializer.data
        })

class SugestaoCompraAPIView(APIView):
    """Calcula quanto comprar de cada item para estoque de segurança"""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        insumos_baixos = Insumo.objects.filter(quantidade_atual__lte=F('nivel_critico'))
        sugestoes = []

        for item in insumos_baixos:
            # Sugere repor até o dobro do nível crítico
            quantidade_sugerida = (item.nivel_critico * 2) - item.quantidade_atual
            sugestoes.append({
                "insumo": item.nome,
                "estoque_atual": item.quantidade_atual,
                "unidade": item.unidade_medida,
                "quantidade_a_comprar": max(round(quantidade_sugerida, 2), 0),
                "fornecedor_contato": item.fornecedor.telefone if item.fornecedor else "Sem fornecedor"
            })

        return Response(sugestoes)

# --- VIEW DE TEMPLATE (HTML) ---

def painel_preparo(request):
    """Renderiza a página HTML do painel de estoque"""
    # .select_related ajuda a carregar os nomes dos fornecedores mais rápido
    insumos = Insumo.objects.all().select_related('fornecedor').order_by('nome')
    return render(request, 'estoque/painel.html', {'insumos': insumos})
