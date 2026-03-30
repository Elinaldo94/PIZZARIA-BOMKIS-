from django.db import models
from vendas.models import Pizza

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self): 
        return self.nome

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

class Insumo(models.Model):
    UNIDADES = [('kg', 'Quilograma'), ('un', 'Unidade'), ('lt', 'Litro')]
    nome = models.CharField(max_length=100)
    quantidade_atual = models.FloatField()
    nivel_critico = models.FloatField()
    unidade_medida = models.CharField(max_length=2, choices=UNIDADES)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True)
    
    # Importante para o seu controle de reposição (TSI)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return f"{self.nome} ({self.quantidade_atual}{self.unidade_medida})"

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

class ReceitaPizza(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade_usada = models.FloatField(help_text="Quantidade necessária para uma pizza média")

    class Meta:
        # Força o Django a criar todas as permissões, incluindo a de visualização (view)
        default_permissions = ('add', 'change', 'delete', 'view')
        verbose_name = "Receita de Pizza"
        verbose_name_plural = "Receitas de Pizzas"

    def __str__(self):
        return f"Receita: {self.pizza.nome} - {self.insumo.nome}"