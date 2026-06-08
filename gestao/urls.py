from django.urls import path
from . import views

urlpatterns = [
    # Rota para a PÁGINA do Dashboard (HTML) - Adicione se não tiver
    path('dashboard/', views.dashboard_gerencial, name='dashboard'), 
    
    path('api/dashboard/', views.DashboardBIAPIView.as_view(), name='api_dashboard'),
    path('api/escala/<str:data_escala>/', views.GestaoEscalaAPIView.as_view(), name='api_gestao_escala'),
    path('equipe/', views.gestao_equipe_view, name='gestao_equipe'),
]
