from django.test import TestCase
from django.utils import timezone
from .models import Pedido

class ProducaoTestCase(TestCase):
    def setUp(self):
        # Criando um pedido Online (Normal)
        self.pedido_online = Pedido.objects.create(
            cliente_nome_avulso="Cliente Web",
            horario_retirada_agendada=timezone.now(),
            prioridade=False
        )
        # Criando um pedido por Telefone (Prioritário)
        self.pedido_telefone = Pedido.objects.create(
            cliente_nome_avulso="Cliente Telefone",
            horario_retirada_agendada=timezone.now(),
            prioridade=True
        )

    def test_prioridade_na_fila(self):
        """Verifica se o pedido por telefone aparece primeiro na consulta"""
        fila = Pedido.objects.order_by('-prioridade', 'horario_pedido')
        self.assertEqual(fila[0].prioridade, True)
        self.assertEqual(fila[0].cliente_nome_avulso, "Cliente Telefone")
