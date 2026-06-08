from rest_framework import serializers
from .models import Insumo, Fornecedor, RegistroCompra

class InsumoSerializer(serializers.ModelSerializer):
    status_critico = serializers.SerializerMethodField()

    class Meta:
        model = Insumo
        fields = '__all__'

    def get_status_critico(self, obj):
        return obj.quantidade_atual <= obj.nivel_critico

class RegistroCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroCompra
        fields = '__all__'
