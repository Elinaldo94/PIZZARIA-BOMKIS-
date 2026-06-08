from rest_framework import serializers
from .models import Funcionario, EscalaTrabalho

class FuncionarioSerializer(serializers.ModelSerializer):
    nome_completo = serializers.CharField(source='usuario.get_full_name', read_only=True)
    class Meta:
        model = Funcionario
        fields = ['id', 'nome_completo', 'funcao', 'telefone', 'ativo']

class EscalaSerializer(serializers.ModelSerializer):
    equipe = FuncionarioSerializer(source='funcionarios', many=True, read_only=True)
    class Meta:
        model = EscalaTrabalho
        fields = ['id', 'data', 'tipo_dia', 'equipe', 'observacoes']

class DashboardSerializer(serializers.Serializer):
    faturamento_bruto = serializers.DecimalField(max_digits=10, decimal_places=2)
    lucro_liquido_projetado = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_pedidos = serializers.IntegerField()
    ranking_pizzas = serializers.ListField()
