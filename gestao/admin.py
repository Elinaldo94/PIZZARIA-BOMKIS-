from django.contrib import admin
from .models import Funcionario, EscalaTrabalho, FeedbackCliente

admin.site.register(Funcionario)
admin.site.register(EscalaTrabalho)
admin.site.register(FeedbackCliente)