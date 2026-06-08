from django.db import models
from django.contrib.auth.models import User

class Funcionario(models.Model):
    FUNCOES = [
        ('preparo', 'Preparo/Massa'),
        ('cozinha', 'Pizzaiolo'),
        ('gerencia', 'Gerente de Pedidos'),
        ('entrega', 'Entregador')
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='funcionario_perfil')
    funcao = models.CharField(max_length=20, choices=FUNCOES)
    telefone = models.CharField(max_length=15)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.get_funcao_display()})"

class EscalaTrabalho(models.Model):
    TIPO_DIA = [('util', 'Dia Útil'), ('fds', 'Fim de Semana'), ('feriado', 'Feriado')]
    data = models.DateField(unique=True)
    tipo_dia = models.CharField(max_length=10, choices=TIPO_DIA)
    funcionarios = models.ManyToManyField(Funcionario, related_name='escalas')
    observacoes = models.TextField(blank=True, help_text="Ex: Substituição por falta de João")

    def __str__(self):
        return f"Escala {self.data} ({self.get_tipo_dia_display()})"
