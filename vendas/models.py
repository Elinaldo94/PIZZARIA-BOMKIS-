from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    def __str__(self): return self.nome

class Pizza(models.Model):
    TAMANHOS = [('P', 'Pequena'), ('M', 'Média'), ('G', 'Grande'), ('F', 'Família')]
    nome = models.CharField(max_length=100)
    ingredientes = models.TextField(verbose_name="Ingredientes")
    preco_p = models.DecimalField(max_digits=6, decimal_places=2)
    preco_m = models.DecimalField(max_digits=6, decimal_places=2)
    preco_g = models.DecimalField(max_digits=6, decimal_places=2)
    disponivel = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.nome} ({self.categoria})"

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    endereco = models.TextField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.usuario.get_full_name() or self.usuario.username