from django.test import TestCase
from .models import Insumo, RegistroCompra

class EstoqueTestCase(TestCase):
    def setUp(self):
        self.insumo = Insumo.objects.create(
            nome="Mussarela", 
            quantidade_atual=10, 
            nivel_critico=5, 
            unidade_medida='kg'
        )

    def test_atualizacao_estoque_apos_compra(self):
        """Verifica se o método save do RegistroCompra atualiza o Insumo"""
        RegistroCompra.objects.create(
            insumo=self.insumo,
            quantidade=5,
            valor_pago=150.00
        )
        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.quantidade_atual, 15)
