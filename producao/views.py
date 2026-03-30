import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Pedido
from vendas.models import Pizza, Cliente

@csrf_exempt
def api_criar_pedido(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'erro': 'Você precisa estar logado'}, status=401)
        
        try:
            data = json.loads(request.body)
            pizzas_ids = data.get('pizzas', []) # Ex: [1, 2]
            
            # Tenta buscar o perfil de Cliente do usuário logado
            try:
                cliente_perfil = request.user.cliente
            except Cliente.DoesNotExist:
                return JsonResponse({'erro': 'Usuário não possui perfil de Cliente'}, status=400)

            # Cria o pedido base
            novo_pedido = Pedido.objects.create(
                cliente=cliente_perfil,
                horario_retirada_agendada=timezone.now() + timezone.timedelta(minutes=30),
                metodo_pagamento=data.get('pagamento', 'online'),
                status='recebido'
            )

            # Adiciona as pizzas ao pedido (M2M Relationship)
            pizzas_objetos = Pizza.objects.filter(id__in=pizzas_ids)
            novo_pedido.pizzas.set(pizzas_objetos)
            novo_pedido.save()

            return JsonResponse({
                'msg': 'Pedido realizado!', 
                'pedido_id': novo_pedido.id,
                'total_pizzas': pizzas_objetos.count()
            }, status=201)

        except Exception as e:
            return JsonResponse({'erro': str(e)}, status=400)

@csrf_exempt
def api_listar_meus_pedidos(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'erro': 'Não logado'}, status=401)
        
        pedidos = Pedido.objects.filter(cliente__usuario=request.user).values(
            'id', 'status', 'horario_pedido', 'metodo_pagamento'
        )
        return JsonResponse(list(pedidos), safe=False)