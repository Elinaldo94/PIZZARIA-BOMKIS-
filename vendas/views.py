import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Pizza, Categoria, Cliente
from producao.models import Pedido  
from producao.models import Pedido
from .models import Cliente
from datetime import datetime, timedelta
from django.utils import timezone # Melhor usar o timezone do Django

def novo_pedido_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        pizza_id = request.POST.get('pizza_id')
        metodo_pagamento = request.POST.get('metodo_pagamento')
        
        try:
            # 1. Busca o Perfil (Gaveta Cliente)
            cliente = Cliente.objects.get(usuario=request.user)
            pizza_escolhida = Pizza.objects.get(id=pizza_id)
            
            # 2. Define a Previsão (Campo OBRIGATÓRIO no seu model producao)
            previsao = timezone.now() + timedelta(minutes=40)
            
            # 3. Cria o objeto Pedido
            # IMPORTANTE: Usei os nomes EXATOS dos campos do seu producao/models.py
            novo_pedido = Pedido.objects.create(
                cliente=cliente,
                metodo_pagamento=metodo_pagamento,
                horario_retirada_agendada=previsao, 
                status='recebido',
                prioridade=False
            )
            
            # 4. Vincula a Pizza (ManyToManyField exige o método .add)
            novo_pedido.pizzas.add(pizza_escolhida)
            
            messages.success(request, f"Sucesso! Pedido #{novo_pedido.id} enviado para a cozinha.")
            
        except Cliente.DoesNotExist:
            messages.error(request, "Erro: Seu usuário não tem um perfil de Cliente. Registre-se novamente.")
        except Exception as e:
            # Isso vai imprimir o erro real no seu terminal (VS Code)
            print(f"--- ERRO NO BANCO: {e} ---") 
            messages.error(request, f"Erro no Banco de Dados: {e}")
            
        return redirect('home_cliente')

    return redirect('home_cliente')

def login_view(request):
    """Exibe a tela de login e processa a autenticação."""
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(username=u, password=p)
        
        if user is not None:
            auth_login(request, user)

            return redirect('home_cliente') 
        else:
            messages.error(request, "Usuário ou senha incorretos.")
            
    return render(request, 'login/login.html')

# vendas/views.py
def home_cliente_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    pedidos = Pedido.objects.filter(cliente__usuario=request.user).order_by('-horario_pedido')
    
    # NÃO ESQUEÇA ESTA LINHA:
    todas_as_pizzas = Pizza.objects.filter(disponivel=True)
    
    return render(request, 'vendas/home.html', {
        'pedidos': pedidos,
        'pizzas': todas_as_pizzas  # Passando as pizzas para o template
    })

def registrar_view(request):
    """Processa o cadastro de novos usuários e perfis de cliente."""
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        t = request.POST.get('telefone')
        e = request.POST.get('endereco')
        
        try:
            # Criação do User (Auth)
            novo_user = User.objects.create_user(username=u, password=p)
            # Criação do Perfil vinculado (Negócio)
            Cliente.objects.create(usuario=novo_user, telefone=t, endereco=e)
            
            messages.success(request, "Conta criada com sucesso! Faça o login.")
            return redirect('login')
        except Exception as err:
            messages.error(request, f"Erro ao cadastrar: {err}")
            
    return render(request, 'vendas/registrar.html')

def logout_view(request):
    """Encerra a sessão e limpa as mensagens."""
    logout(request)
    messages.info(request, "Você saiu do sistema.")
    return redirect('login')


# --- 2. API JSON (PARA TESTES E CONSUMO EXTERNO) ---

@csrf_exempt
def api_registrar_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create_user(
                username=data['username'], 
                password=data['password']
            )
            return JsonResponse({'msg': 'Usuário criado!', 'id': user.id}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                auth_login(request, user)
                return JsonResponse({'status': 'logado', 'usuario': user.username})
            return JsonResponse({'erro': 'Credenciais inválidas'}, status=401)
        except:
            return JsonResponse({'erro': 'Formato JSON inválido'}, status=400)

@csrf_exempt
def api_pizzas(request):
    """Retorna o cardápio em formato JSON conforme solicitado."""
    if request.method == 'GET':
        pizzas = Pizza.objects.all().values('id', 'nome', 'preco_m', 'disponivel')
        return JsonResponse(list(pizzas), safe=False)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            categoria = Categoria.objects.first() 
            if not categoria:
                return JsonResponse({'erro': 'Cadastre uma Categoria no Admin primeiro!'}, status=400)
            
            nova_pizza = Pizza.objects.create(
                nome=data['nome'],
                ingredientes=data.get('ingredientes', ''),
                preco_p=data['preco'], 
                preco_m=data['preco'], 
                preco_g=data['preco'],
                categoria=categoria
            )
            return JsonResponse({'msg': 'Pizza criada!', 'id': nova_pizza.id}, status=201)
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

@csrf_exempt
def api_pizza_detalhe(request, pk):
    pizza = get_object_or_404(Pizza, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': pizza.id, 'nome': pizza.nome, 'ingredientes': pizza.ingredientes, 'preco_m': str(pizza.preco_m)
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pizza.nome = data.get('nome', pizza.nome)
            pizza.ingredientes = data.get('ingredientes', pizza.ingredientes)
            pizza.save()
            return JsonResponse({'msg': 'Pizza atualizada com sucesso!'})
        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

    if request.method == 'DELETE':
        pizza.delete()
        return JsonResponse({'msg': f'Pizza {pk} removida do sistema.'}, status=200)
    
def cancelar_pedido_view(request, pk):
    """Lógica para EXCLUIR (Cancelar) um pedido."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Busca o pedido garantindo que ele pertença ao cliente logado (Segurança)
    pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
    
    # Em vez de deletar fisicamente, você pode apenas mudar o status 
    # ou deletar de fato:
    pedido.delete()
    
    messages.warning(request, f"Pedido #{pk} cancelado com sucesso.")
    return redirect('home_cliente')

def editar_pedido_view(request, pk):
    """Lógica para ATUALIZAR um pedido (Exemplo simplificado)."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
    
    if request.method == "POST":
        # Aqui você capturaria os novos dados do formulário de edição
        metodo = request.POST.get('metodo_pagamento')
        if metodo:
            pedido.metodo_pagamento = metodo
            pedido.save()
            messages.success(request, "Pedido atualizado!")
            return redirect('home_cliente')
            
    return render(request, 'vendas/editar_pedido.html', {'pedido': pedido})