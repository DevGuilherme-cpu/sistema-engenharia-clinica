from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', views.sair, name='logout'),
    
    path('', views.dashboard, name='dashboard'),
    path('equipamentos/', views.listar_equipamentos, name='equipamentos'),
    path('equipamento/cadastrar/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('equipamentos/visualizar/<int:id>/', views.visualizar_equipamento, name='visualizar_equipamento'),
    path('equipamentos/editar/<int:id>/', views.editar_equipamento, name='editar_equipamento'),
    
    path('manutencoes/', views.listar_manutencoes, name='listar_manutencoes'),
    path('manutencoes/nova/', views.cadastrar_manutencao, name='cadastrar_manutencao'),
]