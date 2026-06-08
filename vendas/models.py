from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, help_text="Usado para filtros na API (ex: 'doces')")

    def __str__(self): return self.nome

class Ingrediente(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_estoque = models.IntegerField(default=0)
    nivel_critico = models.IntegerField(default=5, help_text="Gera alerta se atingir este valor")

    def __str__(self): return f"{self.nome} ({self.quantidade_estoque} un)"

class Pizza(models.Model):
    nome = models.CharField(max_length=100)
    ingredientes = models.TextField(verbose_name="Ingredientes Base")
    preco_p = models.DecimalField(max_digits=6, decimal_places=2)
    preco_m = models.DecimalField(max_digits=6, decimal_places=2)
    preco_g = models.DecimalField(max_digits=6, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='pizzas')
    imagem = models.ImageField(upload_to='pizzas/', blank=True, null=True) # Para o cardápio visual
    
    def __str__(self): return self.nome

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    telefone = models.CharField(max_length=15)
    endereco = models.TextField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.usuario.username

# TABELA DE LIGAÇÃO PARA CUSTOMIZAÇÃO (Requisito: escolha de ingredientes e tamanho)
class ItemPedido(models.Model):
    TAMANHOS = [('P', 'Pequena'), ('M', 'Média'), ('G', 'Grande')]
    pedido = models.ForeignKey('producao.Pedido', on_delete=models.CASCADE, related_name='itens')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    tamanho = models.CharField(max_length=1, choices=TAMANHOS)
    ingredientes_adicionais = models.ManyToManyField(Ingrediente, blank=True)

class Avaliacao(models.Model):
    pedido = models.OneToOneField('producao.Pedido', on_delete=models.CASCADE, related_name='avaliacao')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nota = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
        