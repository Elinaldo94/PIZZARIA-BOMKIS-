from django.test import TestCase
from django.contrib.auth.models import User
from .models import Funcionario, EscalaTrabalho
from datetime import date

class GestaoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="pizzaiolo1", first_name="Mario")
        self.funcionario = Funcionario.objects.create(
            usuario=self.user, 
            funcao='cozinha', 
            telefone='123456'
        )

    def test_criacao_escala(self):
        """Verifica se a escala está associando funcionários corretamente"""
        escala = EscalaTrabalho.objects.create(
            data=date(2023, 12, 31),
            tipo_dia='feriado'
        )
        escala.funcionarios.add(self.funcionario)
        self.assertEqual(escala.funcionarios.count(), 1)
        self.assertEqual(escala.tipo_dia, 'feriado')
