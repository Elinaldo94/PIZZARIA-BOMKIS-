from django.db import models
from vendas.models import Pizza

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self): return self.nome

class Insumo(models.Model):
    UNIDADES = [('kg', 'Quilograma'), ('un', 'Unidade'), ('lt', 'Litro')]
    nome = models.CharField(max_length=100)
    quantidade_atual = models.FloatField(default=0)
    nivel_critico = models.FloatField(default=5)
    unidade_medida = models.CharField(max_length=2, choices=UNIDADES)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return f"{self.nome} ({self.quantidade_atual}{self.unidade_medida})"

class ReceitaPizza(models.Model):
    """Define quanto de cada insumo uma pizza consome (Ficha Técnica)"""
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, related_name='receita')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade_usada = models.FloatField(help_text="Qtd para uma pizza média")

    def __str__(self):
        return f"{self.pizza.nome} utiliza {self.quantidade_usada} de {self.insumo.nome}"

class RegistroCompra(models.Model):
    """Requisito: Registro de compras e fornecedores"""
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade = models.FloatField()
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.insumo.quantidade_atual += self.quantidade
        self.insumo.save()
        super().save(*args, **kwargs)

class AlertaEstoque(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    data_alerta = models.DateTimeField(auto_now_add=True)
    resolvido = models.BooleanField(default=False)
    mensagem = models.TextField()

    def __str__(self):
        return f"ALERTA: {self.insumo.nome} em {self.data_alerta.strftime('%d/%m')}"
