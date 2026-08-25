import json
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Equipamento, Manutencao, Setor, TrocaAcessorio
from .forms import ManutencaoForm

@login_required
def dashboard(request):
    total_equipamentos = Equipamento.objects.count()
    operacionais = Equipamento.objects.filter(status='funcionamento').count()
    em_manutencao = Equipamento.objects.filter(status='manutencao').count()
    
    status_labels = ['Em Funcionamento', 'Em Manutenção', 'Não Localizados / Outros']
    status_data = [operacionais, em_manutencao, total_equipamentos - operacionais - em_manutencao]

    top_fabricantes = Equipamento.objects.values('marca').annotate(total=Count('id')).order_by('-total')[:5]
    fab_labels = [item['marca'] if item['marca'] else 'Sem Marca' for item in top_fabricantes]
    fab_data = [item['total'] for item in top_fabricantes]

    contexto = {
        'active_page': 'dashboard',
        'total_equipamentos': total_equipamentos,
        'operacionais': operacionais,
        'em_manutencao': em_manutencao,
        'status_labels': status_labels,
        'status_data': status_data,
        'fab_labels': fab_labels,
        'fab_data': fab_data,
    }
    return render(request, 'index.html', contexto)

@login_required
def listar_equipamentos(request):
    equipamentos = Equipamento.objects.select_related('setor').all()
    return render(request, 'Equipamentos/equipamentos.html', 
                  {'active_page': 'equipamentos', 
                   'equipamentos': equipamentos
                   })

@login_required
def cadastrar_equipamento(request):
    if request.method == 'POST':
        patrimonio = request.POST.get('patrimonio')
        numero_serie = request.POST.get('numero_serie')
        descricao = request.POST.get('descricao')
        setor_id = request.POST.get('setor')
        status = request.POST.get('status')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        observacoes = request.POST.get('observacoes')

        setor = get_object_or_404(Setor, id=setor_id)

        Equipamento.objects.create(
            patrimonio=patrimonio,
            numero_serie=numero_serie,
            descricao=descricao,
            setor=setor,
            status=status,
            marca=marca,
            modelo=modelo,
            observacoes=observacoes
        )
        return redirect('equipamentos')
    
    setores = Setor.objects.all()
    return render(request, 'Equipamentos/cadastrar_equipamento.html', {'active_page': 'equipamentos', 'setores': setores})

@login_required
def visualizar_equipamento(request, id):
    equipamento = get_object_or_404(Equipamento, id=id)
    manutencoes = Manutencao.objects.filter(equipamento=equipamento).order_by('-data_execucao')
    return render(request, 'Equipamentos/visualizar.html', {'active_page': 'equipamentos', 'equipamento': equipamento, 'manutencoes': manutencoes})

@login_required
def editar_equipamento(request, id):
    equipamento = get_object_or_404(Equipamento, id=id)
    if request.method == 'POST':
        equipamento.patrimonio = request.POST.get('patrimonio')
        equipamento.numero_serie = request.POST.get('numero_serie')
        equipamento.descricao = request.POST.get('descricao')
        
        setor_id = request.POST.get('setor')
        if setor_id:
            equipamento.setor = get_object_or_404(Setor, id=setor_id)
            
        equipamento.status = request.POST.get('status')
        equipamento.marca = request.POST.get('marca')
        equipamento.modelo = request.POST.get('modelo')
        equipamento.observacoes = request.POST.get('observacoes')
        
        equipamento.save()
        return redirect('visualizar_equipamento', id=equipamento.id)
    
    setores = Setor.objects.all()
    return render(request, 'Equipamentos/editar_equipamento.html', {'active_page': 'equipamentos', 'equipamento': equipamento, 'setores': setores})

@login_required
def listar_manutencoes(request):
    manutencoes = Manutencao.objects.select_related('equipamento').all().order_by('-data_execucao')
    return render(request, 'Manutencoes/manutencoes.html', {'active_page': 'manutencoes', 'manutencoes': manutencoes})

@login_required
def cadastrar_manutencao(request):
    if request.method == 'POST':
        equipamento_id = request.POST.get('equipamento')
        tipo_manutencao = request.POST.get('tipo_manutencao')
        data_execucao = request.POST.get('data_execucao')
        tecnico = request.POST.get('tecnico')
        status = request.POST.get('status')
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')

        equipamento = get_object_or_404(Equipamento, id=equipamento_id)

        Manutencao.objects.create(
            equipamento=equipamento,
            tipo_manutencao=tipo_manutencao,
            data_execucao=data_execucao,
            tecnico=tecnico,
            status=status,
            titulo=titulo,
            descricao=descricao
        )
        return redirect('visualizar_equipamento', id=equipamento.id)
    
    equipamento_id_url = request.GET.get('equipamento', '')
    tipo_url = request.GET.get('tipo', '').lower()

    equipamentos = Equipamento.objects.all()
    return render(request, 'Manutencoes/cadastrar.html', {
        'active_page': 'manutencoes', 
        'equipamentos': equipamentos, 
        'equipamento_id_url': equipamento_id_url,
        'tipo_url': tipo_url,
        })

@login_required
def listar_acessorios(request):
    trocas = TrocaAcessorio.objects.select_related('equipamento').all().order_by('-data_troca')
    return render(request, 'Acessorios/acessorios.html', {
        'active_page': 'acessorios', 
        'trocas': trocas
    })

@login_required
def registrar_troca(request):
    if request.method == 'POST':
        equipamento_id = request.POST.get('equipamento')
        nome_acessorio = request.POST.get('nome_acessorio')
        data_troca = request.POST.get('data_troca')
        motivo = request.POST.get('motivo')
        tecnico = request.POST.get('tecnico')

        equipamento = get_object_or_404(Equipamento, id=equipamento_id)
        
        TrocaAcessorio.objects.create(
            equipamento=equipamento,
            nome_acessorio=nome_acessorio,
            data_troca=data_troca,
            motivo=motivo,
            tecnico=tecnico
        )
        return redirect('acessorios') 
    
    equipamentos = Equipamento.objects.all()
    return render(request, 'Acessorios/registrar_troca.html', {
        'active_page': 'acessorios', 
        'equipamentos': equipamentos
    })

@login_required
def relatorio_marcas(request):
    marca_selecionada = request.GET.get('marca', '')
    
    marcas_existentes = Equipamento.objects.values_list('marca', flat=True).distinct().order_by('marca')
    
    if marca_selecionada:
        equipamentos = Equipamento.objects.select_related('setor').filter(marca=marca_selecionada)
    else:
        equipamentos = Equipamento.objects.select_related('setor').all()
        
    total = equipamentos.count()
    em_funcionamento = equipamentos.filter(status='funcionamento').count()
    em_manutencao = equipamentos.filter(status='manutencao').count()

    contexto = {
        'active_page': 'relatorios',
        'marcas': marcas_existentes,
        'marca_selecionada': marca_selecionada,
        'equipamentos': equipamentos,
        'total': total,
        'em_funcionamento': em_funcionamento,
        'em_manutencao': em_manutencao,
    }
    return render(request, 'Relatorios/relatorio_marcas.html', contexto)

@login_required
def cadastrar_usuario(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard')

    mensagem = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        nome = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        eh_admin = request.POST.get('is_staff') == 'on'

        if User.objects.filter(username=username).exists():
            mensagem = "Erro: Este nome de usuário já está em uso!"
        else:
            novo_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nome
            )
            if eh_admin:
                novo_user.is_staff = True
                novo_user.is_superuser = True
            novo_user.save()
            return redirect('dashboard')

    return render(request, 'Usuarios/cadastrar.html', {'active_page': 'admin', 'mensagem': mensagem})

def sair(request):
    logout(request)
    return redirect('login')