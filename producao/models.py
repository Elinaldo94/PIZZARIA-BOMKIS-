from django.db import models
from vendas.models import Pizza, Cliente

class Pedido(models.Model):
    # Status atualizados para incluir o fluxo de entrega (Logística)
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
    
    # Vinculação com Cliente (Cadastro) ou Nome Avulso (Telefone)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    cliente_nome_avulso = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Para pedidos por telefone sem cadastro"
    )
    
    pizzas = models.ManyToManyField(Pizza)
    
    # Datas e Horários (Rastreabilidade de TSI)
    horario_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Hora da Compra")
    horario_retirada_agendada = models.DateTimeField(verbose_name="Previsão de Entrega/Retirada")
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    # Controle Operacional
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recebido')
    metodo_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='online')
    prioridade = models.BooleanField(default=False, help_text="Marque para pedidos prioritários (ex: Telefone)")
    
    def __str__(self):
        identificacao = self.cliente if self.cliente else self.cliente_nome_avulso
        return f"Pedido #{self.id} - {identificacao}"

class Fornada(models.Model):
    pedidos = models.ManyToManyField(Pedido)
    inicio_forno = models.DateTimeField(auto_now_add=True)
    capacidade_maxima = models.IntegerField(default=9)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return f"Fornada {self.id} - Início: {self.inicio_forno.strftime('%H:%M')}"