from rest_framework import serializers
from .models import Pedido, Fornada

class FornadaSerializer(serializers.ModelSerializer):
    tempo_restante = serializers.SerializerMethodField()

    class Meta:
        model = Fornada
        fields = '__all__'

    def get_tempo_restante(self, obj):
        if obj.concluida: return 0
        restante = obj.previsao_conclusao - timezone.now()
        return max(int(restante.total_seconds() / 60), 0)
