import json
import datetime
from datetime import timedelta

from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateparse import parse_time  # Unificado aqui
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout 

# CORE DO REST FRAMEWORK (Uso único de cada classe)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

# MODELOS E SERIALIZERS DO SEU ECOSSISTEMA
from .models import Pizza, Categoria, Cliente, Ingrediente, ItemPedido, Avaliacao
from .serializers import (
    AvaliacaoSerializer, PerfilClienteSerializer, RegistroUsuarioSerializer,
    PizzaSerializer, NovoPedidoSerializer
)
from producao.models import Pedido


def home_cliente_view(request):

    # Buscamos apenas as pizzas para renderizar as opções do formulário nativo na página
    from vendas.models import Pizza
    pizzas = Pizza.objects.filter(disponivel=True)
    
    return render(request, 'vendas/home.html', {
        'pizzas': pizzas
    })



def logout_view(request):
    logout(request) # Isso limpa a sessão do usuário no servidor e no navegador
    return redirect('login') # Te manda de volta para a tela de login


def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            auth_login(request, user) # CRIA A SESSÃO
            return redirect('home_cliente') 
        else:
            messages.error(request, "Usuário ou senha inválidos.")
            
    return render(request, 'login/login.html')

class MeusPedidosAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pedidos = Pedido.objects.filter(
            cliente__usuario=request.user
        ).order_by('-horario_pedido')
        
        dados = [{
            "id": p.id,
            "data": p.horario_pedido.strftime("%d/%m/%Y"),
            "status": p.get_status_display(),
            "pago": p.pago,
            "previsao_retirada": p.horario_retirada_agendada.strftime("%H:%M"),
            "metodo_pagamento": p.metodo_pagamento
        } for p in pedidos]
        
        return Response(dados, status=status.HTTP_200_OK)


class PizzaDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        pizza = get_object_or_404(Pizza, pk=pk)
        serializer = PizzaSerializer(pizza)
        return Response(serializer.data)

    def put(self, request, pk): 
        pizza = get_object_or_404(Pizza, pk=pk)
        serializer = PizzaSerializer(pizza, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Pizza atualizada com sucesso!", "data": serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pizza = get_object_or_404(Pizza, pk=pk)
        pizza.delete()
        return Response({"msg": f"Pizza {pk} removida do sistema."}, status=status.HTTP_204_NO_CONTENT)


class CancelarPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)

        if pedido.status in ['no_forno', 'pronto', 'entregue']:
            return Response(
                {"erro": f"Não é possível cancelar um pedido com status: {pedido.get_status_display()}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.status = 'cancelado'
        pedido.save()
        
        return Response({"msg": f"Pedido #{pk} cancelado com sucesso."}, status=status.HTTP_200_OK)

class EditarPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk): 
        pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
        

        if pedido.status != 'recebido':
            return Response(
                {"erro": "O pedido já está em produção e não pode mais ser editado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        metodo = request.data.get('metodo_pagamento')
        horario = request.data.get('horario_retirada')

        if metodo:
            pedido.metodo_pagamento = metodo
        if horario:
            pedido.horario_retirada_agendada = horario
        
        pedido.save()
        return Response({"msg": "Pedido atualizado com sucesso!"})

class StatusPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
        
        agora = timezone.now()
        atrasado = agora.time() > pedido.horario_retirada_agendada if pedido.status != 'entregue' else False

        return Response({
            "rastreio": {
                "id": pedido.id,
                "status_atual": pedido.get_status_display(), 
                "status_slug": pedido.status,               
                "pago": pedido.pago,
                "origem": pedido.get_origem_display(),       
                "horario_pedido": pedido.horario_pedido.strftime("%H:%M:%S"),
                "previsao_retirada": pedido.horario_retirada_agendada.strftime("%H:%M"),
                "esta_atrasado": atrasado
            },
            "etapas_producao": {
                "recebido": pedido.status in ['recebido', 'preparo', 'no_forno', 'pronto', 'entregue'],
                "em_preparo": pedido.status in ['preparo', 'no_forno', 'pronto', 'entregue'],
                "no_forno": pedido.status in ['no_forno', 'pronto', 'entregue'],
                "pronto": pedido.status in ['pronto', 'entregue'],
                "concluido": pedido.status == 'entregue'
            },
            "mensagem_status": self._get_status_message(pedido.status)
        }, status=status.HTTP_200_OK)

    def _get_status_message(self, status_slug):
        mensagens = {
            'recebido': "Seu pedido foi recebido e está na fila!",
            'preparo': "Nossos pizzaiolos já estão montando sua pizza!",
            'no_forno': "Sua pizza está no forno, o cheirinho está ótimo!",
            'pronto': "Sua pizza está prontinha! Pode vir retirar.",
            'entregue': "Pedido entregue. Bom apetite!",
            'cancelado': "Este pedido foi cancelado."
        }
        return mensagens.get(status_slug, "Status desconhecido.")


class PagamentoPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
        if pedido.status == 'cancelado':
            return Response({"erro": "Não é possível pagar um pedido cancelado."}, status=status.HTTP_400_BAD_REQUEST)
        
        if pedido.pago:
            return Response({"aviso": "Este pedido já consta como pago no sistema."}, status=status.HTTP_200_OK)
            
        metodo = request.data.get('metodo_pagamento')
        if metodo not in ['cartao_online', 'pix']:
            return Response({"erro": "Método de pagamento online inválido nesta rota."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Busca o preço real da pizza vinculada ao item para evitar o AttributeError
        item_pedido = pedido.itens.first()
        valor_final = 0
        if item_pedido:
            if item_pedido.tamanho == 'P': 
                valor_final = item_pedido.pizza.preco_p
            elif item_pedido.tamanho == 'M': 
                valor_final = item_pedido.pizza.preco_m
            else: 
                valor_final = item_pedido.pizza.preco_g

        try:
            pedido.pago = True
            pedido.metodo_pagamento = metodo
            pedido.save()
            
            return Response({
                "status": "sucesso",
                "mensagem": "Pagamento online aprovado!",
                "detalhes": {
                    "pedido_id": pedido.id,
                    "valor_pago": str(valor_final), # Retornando o valor correto calculado
                    "codigo_transacao": f"BOMKISO-{pedido.id}-{timezone.now().timestamp()}"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"erro": f"Falha no processador de pagamento: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvaliarPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)

        if pedido.status != 'entregue':
            return Response({"erro": "Apenas pedidos entregues podem ser avaliados."}, status=400)
        
        if hasattr(pedido, 'avaliacao'):
            return Response({"erro": "Este pedido já foi avaliado."}, status=400)

        serializer = AvaliacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pedido=pedido, cliente=pedido.cliente)
            return Response({"msg": "Avaliação enviada!", "data": serializer.data}, status=201)
        
        return Response(serializer.errors, status=400)


class PerfilClienteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = PerfilClienteSerializer(request.user.cliente)
        return Response(serializer.data)

    def patch(self, request):
        serializer = PerfilClienteSerializer(request.user.cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Perfil atualizado!", "data": serializer.data})
        
        return Response(serializer.errors, status=400)

class RegistrarUsuarioAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Usuário e Cliente criados!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 1. A CLASSE API (Para o JSON/Postman)
class CardapioAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        pizzas = Pizza.objects.filter(disponivel=True)
        categoria = request.query_params.get('categoria')
        if categoria:
            pizzas = pizzas.filter(categoria__slug=categoria)
        
        serializer = PizzaSerializer(pizzas, many=True)
        return Response(serializer.data)

# 2. A FUNÇÃO HTML (Para abrir a página no navegador)
# Note que ela está FORA da classe acima (encostada na margem esquerda)
def cardapio_view(request):
    pizzas = Pizza.objects.filter(disponivel=True)
    categorias = Categoria.objects.all()
    return render(request, 'vendas/cardapio.html', {
        'pizzas': pizzas, 
        'categorias': categorias
    })



class PizzaListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET': return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def post(self, request):
        serializer = PizzaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NovoPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = NovoPedidoSerializer(data=request.data)
        if serializer.is_valid():
            v = serializer.validated_data
            
            # Captura a string enviada (ex: "20:30")
            horario_str = request.data.get('horario_retirada') or v.get('horaria_retirada')
            
            # Converte o texto em um objeto Time real do Python
            horario_time = parse_time(horario_str) if isinstance(horario_str, str) else horario_str
            
            # Combina com a data de hoje para gerar o Datetime completo exigido pelo banco
            horario_completo = datetime.datetime.combine(datetime.date.today(), horario_time)

            # --- CORREÇÃO DO ERRO 500: Busca tolerante a falhas para o perfil do Cliente ---
            cliente_perfil = Cliente.objects.filter(usuario=request.user).first()
            
            # Se for o usuário admin de teste e não possuir perfil de delivery, cria um automático
            if not cliente_perfil:
                cliente_perfil = Cliente.objects.create(
                    usuario=request.user,
                    telefone="(00) 99999-9999",
                    endereco="Balcão / Área Administrativa"
                )

            # Cria o pedido associando o cliente garantido
            pedido = Pedido.objects.create(
                cliente=cliente_perfil, # Vincula o perfil seguro
                metodo_pagamento=v['metodo_pagamento'],
                horario_retirada_agendada=horario_completo,
                status='recebido',
                origem='online'
            )
            
            pizza = Pizza.objects.get(id=v['pizza_id'])
            item = ItemPedido.objects.create(
                pedido=pedido,
                pizza=pizza,
                tamanho=v['tamanho']
            )
            
            for ing_id in v.get('ingredientes', []):
                try:
                    ingrediente = Ingrediente.objects.get(id=ing_id)
                    item.ingredientes_adicionais.add(ingrediente)
                    ingrediente.quantidade_estoque -= 1
                    ingrediente.save()
                except Ingrediente.DoesNotExist:
                    continue
                    
            return Response({
                "msg": "Pedido realizado com sucesso!",
                "id": pedido.id,
                "previsao": pedido.horario_retirada_agendada.strftime("%H:%M")
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def registrar_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')
        
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "Este nome de usuário já está em uso.")
            return render(request, 'vendas/registrar.html')
        
        user = User.objects.create_user(username=usuario, password=senha)
        
        Cliente.objects.create(usuario=user, telefone=telefone, endereco=endereco)
        
        messages.success(request, "Cadastro realizado com sucesso! Faça seu login.")
        return redirect('login')
        
    return render(request, 'vendas/registrar.html')

class AtualizarStatusPedidoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        novo_status = request.data.get('status', '').lower()

        # DICIONÁRIO DE MAPA: Transforma o texto do JS na sigla real do seu Banco de Dados
        mapeamento = {
            # Se o banco usar palavra inteira:
            'recebido': 'recebido',
            'forno': 'forno',
            'no_forno': 'forno',
            'pronto': 'pronto',
            'concluido': 'concluido',
            
            # Se o banco usar siglas de 3 letras (Padrão de segurança de BD):
            'recebido_sigla': 'REC',
            'forno_sigla': 'FOR',
            'pronto_sigla': 'PRN',
            'concluido_sigla': 'CON'
        }

        # Tenta salvar no formato texto. Se o banco rejeitar, tenta salvar no formato sigla
        status_final = mapeamento.get(novo_status)
        
        try:
            pedido.status = status_final
            pedido.save()
        except Exception:
            # Fallback automático caso o seu modelo use siglas Curtas (REC, FOR, PRN, CON)
            status_sigla = mapeamento.get(f"{novo_status}_sigla")
            if status_sigla:
                pedido.status = status_sigla
                pedido.save()
            else:
                return Response({"erro": "Status incompatível com as diretrizes do banco."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "sucesso",
            "novo_status_banco": pedido.status
        }, status=status.HTTP_200_OK)
