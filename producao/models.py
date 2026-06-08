from django.db import models
from django.utils import timezone
from datetime import timedelta

class Pedido(models.Model):
    # DEFINA AS ESCOLHAS ANTES DE USÁ-LAS NOS CAMPOS
    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('preparo', 'Em preparo'),
        ('forno', 'No forno'),
        ('pronto', 'Pronto para retirada'),
        ('entrega', 'Saiu para entrega'),
        ('concluido', 'Entregue / Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro na Retirada'),
        ('cartao_entrega', 'Cartão na Entrega'),
        ('pix', 'PIX'),
        ('online', 'Pagamento Online'),
    ]

    ORIGEM_CHOICES = [
        ('online', 'Online'), 
        ('telefone', 'Telefone')
    ]
    
    # CAMPOS DO MODELO
    cliente = models.ForeignKey('vendas.Cliente', on_delete=models.CASCADE, null=True, blank=True)
    cliente_nome_avulso = models.CharField(max_length=100, blank=True)
    pizzas = models.ManyToManyField('vendas.Pizza', related_name='pedido')
    
    horario_pedido = models.DateTimeField(auto_now_add=True)
    horario_retirada_agendada = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recebido')
    metodo_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='online')
    origem = models.CharField(max_length=10, choices=ORIGEM_CHOICES, default='online')
    pago = models.BooleanField(default=False)
    prioridade = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido #{self.id}"

class Fornada(models.Model):
    pedidos = models.ManyToManyField(Pedido, related_name='fornadas')
    inicio_forno = models.DateTimeField(auto_now_add=True)
    previsao_conclusao = models.DateTimeField(blank=True, null=True)
    concluida = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.previsao_conclusao:
            self.previsao_conclusao = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
