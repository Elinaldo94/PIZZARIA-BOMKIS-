from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Pizza, Categoria, Cliente, ItemPedido, Ingrediente, Avaliacao
from producao.models import Pedido

# --- PERFIL E CADASTRO ---

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Lógica para criar User e Cliente simultaneamente"""
    telefone = serializers.CharField()
    endereco = serializers.CharField()
    # CORRIGIDO: Forçado explicitamente como write_only para matar o AssertionError do DRF
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'telefone', 'endereco']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        Cliente.objects.create(
            usuario=user,
            telefone=validated_data['telefone'],
            endereco=validated_data['endereco']
        )
        return user

class PerfilClienteSerializer(serializers.ModelSerializer):
    """Exibe dados de conta e entrega integrados"""
    email = serializers.EmailField(source='usuario.email', read_only=False)
    username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Cliente
        fields = ['username', 'email', 'telefone', 'endereco']

    def update(self, instance, validated_data):
        usuario_data = validated_data.pop('usuario', {})
        email = usuario_data.get('email')
        if email:
            instance.usuario.email = email
            instance.usuario.save()
        return super().update(instance, validated_data)

# --- CARDÁPIO ---

class PizzaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Pizza
        fields = [
            'id', 
            'nome', 
            'preco_p', 
            'preco_m', 
            'preco_g', 
            'disponivel', 
            'categoria', 
            'categoria_nome'
        ]
        read_only_fields = ['id'] 


# --- PEDIDOS E AVALIAÇÃO ---

class NovoPedidoSerializer(serializers.Serializer):
    """Valida a entrada de novos pedidos JSON"""
    pizza_id = serializers.IntegerField()
    tamanho = serializers.ChoiceField(choices=['P', 'M', 'G'])
    metodo_pagamento = serializers.CharField()
    horario_retirada = serializers.TimeField(required=False)
    ingredientes = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False
    )

    def validate_pizza_id(self, value):
        if not Pizza.objects.filter(id=value, disponivel=True).exists():
            raise serializers.ValidationError("Pizza não disponível ou inexistente.")
        return value

class AvaliacaoSerializer(serializers.ModelSerializer):
    """Valida feedbacks de clientes"""
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']

    def validate_nota(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("A nota deve estar entre 1 e 5.")
        return value
