from django.db import models
from django.contrib.auth.models import User

class Funcionario(models.Model):
    FUNCOES = [('preparo', 'Preparo'), ('cozinha', 'Cozinha'), ('gerencia', 'Gerência'), ('entrega', 'Entregas')]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    funcao = models.CharField(max_length=20, choices=FUNCOES)
    telefone = models.CharField(max_length=15)
    data_contratacao = models.DateField(auto_now_add=True)

    def __str__(self): return self.usuario.get_full_name() or self.usuario.username

class EscalaTrabalho(models.Model):
    TIPO_DIA = [('util', 'Dia Útil'), ('fds', 'Fim de Semana'), ('feriado', 'Feriado')]
    data = models.DateField()
    tipo_dia = models.CharField(max_length=10, choices=TIPO_DIA)
    funcionarios = models.ManyToManyField(Funcionario)

class FeedbackCliente(models.Model):
    pedido = models.OneToOneField('producao.Pedido', on_delete=models.CASCADE)
    nota = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    data_feedback = models.DateTimeField(auto_now_add=True)