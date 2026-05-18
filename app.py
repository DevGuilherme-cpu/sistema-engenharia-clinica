from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Monitor, Preventiva, ManutencaoExterna, Acessorio, Usuario
from datetime import datetime
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps 
import pandas as pd
from io import BytesIO
from flask import send_file 
import os

app = Flask(__name__)

banco_url = os.getenv('DATABASE_URL', 'postgresql://postgres:GuiLandin@localhost:5432/engenharia_clinica')

if banco_url and banco_url.startswith("postgres://"):
    banco_url = banco_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = banco_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta_super_dificil_aqui'

db.init_app(app)

# Trava de Segurança
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ROTAS DE AUTENTICAÇÃO
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!', 'erro')
            
    if 'usuario_id' in session:
        return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        username = request.form.get('username')
        senha = request.form.get('senha')

        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            flash('Este nome de usuário já está em uso. Escolha outro.', 'erro')
            return redirect(url_for('cadastrar_usuario'))

        senha_criptografada = generate_password_hash(senha)
        
        novo_usuario = Usuario(nome=nome, username=username, senha=senha_criptografada)
        db.session.add(novo_usuario)
        db.session.commit()

        print(f"Usuário {nome} cadastrado com sucesso!")
        return redirect(url_for('index'))

    return render_template('cadastrar_usuario.html')

# ROTAS DO SISTEMA
@app.route('/')
@login_required
def index():
    total = Monitor.query.count()
    completos = Monitor.query.filter_by(status='Completa').count()
    pendentes = Monitor.query.filter_by(status='Pendente').count()
    manutencao = Monitor.query.filter_by(status='Manutenção').count()
    desaparecidos = Monitor.query.filter_by(status='Desaparecido').count()
    marcas_db = db.session.query(Monitor.marca, func.count(Monitor.id)).group_by(Monitor.marca).all() 
    nomes_marcas = [m[0] if m[0] else 'Sem Marca' for m in marcas_db]
    qtd_marcas = [m[1] for m in marcas_db]
    
    return render_template(
        'index.html', 
        total=total, completos=completos, pendentes=pendentes, 
        manutencao=manutencao, desaparecidos=desaparecidos,
        nomes_marcas=nomes_marcas, qtd_marcas=qtd_marcas
    )

@app.route('/cadastrar_monitor', methods=['GET', 'POST'])
@login_required
def cadastrar_monitor():
    if request.method == 'POST':
        novo_monitor = Monitor(
            descricao=request.form.get('descricao'),
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            numero_serie=request.form.get('numero_serie'),
            patrimonio=request.form.get('patrimonio'),
            local=request.form.get('local'),
            status=request.form.get('status'),
            empresa=request.form.get('empresa'),
            contrato=request.form.get('contrato')
        )

        db.session.add(novo_monitor)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('cadastrar_monitor.html')


@app.route('/monitores')
@login_required
def listar_monitores():
    marca_filtro = request.args.get('marca')
    marcas_db = db.session.query(Monitor.marca).filter(
        Monitor.marca.isnot(None), Monitor.marca != '').distinct().all()
    marcas_unicas = sorted([m[0] for m in marcas_db])
    query = Monitor.query.order_by(Monitor.descricao.asc())

    if marca_filtro:
        query = query.filter(Monitor.marca == marca_filtro)

    todos_monitores = query.all()

    return render_template('monitores.html',
                           monitores=todos_monitores,
                           marcas=marcas_unicas,
                           marca_atual=marca_filtro)


@app.route('/excluir_monitor/<int:id>')
@login_required
def excluir_monitor(id):
    monitor = Monitor.query.get_or_404(id)
    db.session.delete(monitor)
    db.session.commit()
    return redirect(url_for('listar_monitores'))


@app.route('/editar_monitor/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_monitor(id):
    monitor = Monitor.query.get_or_404(id)

    if request.method == 'POST':
        monitor.descricao = request.form.get('descricao')
        monitor.marca = request.form.get('marca')
        monitor.modelo = request.form.get('modelo')
        monitor.numero_serie = request.form.get('numero_serie')
        monitor.patrimonio = request.form.get('patrimonio')
        monitor.local = request.form.get('local')
        monitor.status = request.form.get('status')
        monitor.empresa = request.form.get('empresa')

        db.session.commit()
        return redirect(url_for('listar_monitores'))

    return render_template('editar_monitor.html', monitor=monitor)


@app.route('/cadastrar_preventiva', methods=['GET', 'POST'])
@login_required
def cadastrar_preventiva():
    if request.method == 'POST':
        monitor_id = request.form.get('monitor_id')
        data_str = request.form.get('data_preventiva')
        mes = request.form.get('mes')
        responsavel = request.form.get('responsavel')
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()

        nova_preventiva = Preventiva(
            monitor_id=monitor_id,
            data_preventiva=data_obj,
            mes=mes,
            responsavel=responsavel
        )
        db.session.add(nova_preventiva)

        monitor = Monitor.query.get(monitor_id)
        if monitor:
            monitor.status = 'Completa'

        db.session.commit()

        return redirect(url_for('index'))

    todos_monitores = Monitor.query.all()
    return render_template('cadastrar_preventiva.html', monitores=todos_monitores)


@app.route('/historico_preventivas')
@login_required
def historico_preventivas():
    todas_preventivas = Preventiva.query.order_by(
        Preventiva.data_preventiva.desc()).all()
    return render_template('historico_preventivas.html', preventivas=todas_preventivas)


@app.route('/nova_corretiva', methods=['GET', 'POST'])
@login_required
def nova_corretiva():
    if request.method == 'POST':
        monitor_id = request.form.get('monitor_id')
        motivo = request.form.get('motivo')
        empresa = request.form.get('empresa')
        data_saida_str = request.form.get('data_saida')
        previsao_str = request.form.get('previsao_retorno')
        data_saida = datetime.strptime(data_saida_str, '%Y-%m-%d').date()
        previsao = datetime.strptime(
            previsao_str, '%Y-%m-%d').date() if previsao_str else None

        nova_corretiva = ManutencaoExterna(
            monitor_id=monitor_id,
            motivo=motivo,
            empresa=empresa,
            data_saida=data_saida,
            previsao_retorno=previsao
        )
        db.session.add(nova_corretiva)

        monitor = Monitor.query.get(monitor_id)
        if monitor:
            monitor.status = 'Manutenção'

        db.session.commit()
        return redirect(url_for('index'))

    monitores_disponiveis = Monitor.query.filter(
        Monitor.status != 'Manutenção').all()
    return render_template('nova_corretiva.html', monitores=monitores_disponiveis)


@app.route('/retorno_corretiva', methods=['GET', 'POST'])
@login_required
def retorno_corretiva():
    if request.method == 'POST':
        manutencao_id = request.form.get('manutencao_id')
        data_retorno_str = request.form.get('data_retorno')
        tecnico = request.form.get('tecnico')
        manutencao = ManutencaoExterna.query.get(manutencao_id)

        if manutencao:
            manutencao.data_retorno = datetime.strptime(
                data_retorno_str, '%Y-%m-%d').date()
            manutencao.tecnico = tecnico
            manutencao.status = 'Concluída'

            monitor = Monitor.query.get(manutencao.monitor_id)
            if monitor:
                monitor.status = 'Completa'

            db.session.commit()

        return redirect(url_for('index'))

    manutencoes_pendentes = ManutencaoExterna.query.filter_by(
        status='Aguardando Retorno').all()
    return render_template('retorno_corretiva.html', manutencoes=manutencoes_pendentes)


@app.route('/historico_corretivas')
@login_required
def historico_corretivas():
    todas_corretivas = ManutencaoExterna.query.order_by(
        ManutencaoExterna.data_saida.desc()).all()
    return render_template('historico_corretivas.html', manutencoes=todas_corretivas)

@app.route('/acessorios')
@login_required
def historico_acessorios():
    todas_trocas = Acessorio.query.order_by(Acessorio.data_troca.desc()).all()
    return render_template('acessorios.html', acessorios=todas_trocas)

@app.route('/novo_acessorio', methods=['GET', 'POST'])
@login_required
def novo_acessorio():
    if request.method == 'POST':
        monitor_id = request.form.get('monitor_id')
        tipo = request.form.get('tipo')
        data_troca_str = request.form.get('data_troca')
        data_troca = datetime.strptime(data_troca_str, '%Y-%m-%d').date()

        nova_troca = Acessorio(
            monitor_id=monitor_id,
            tipo=tipo,
            data_troca=data_troca
        )
        db.session.add(nova_troca)
        db.session.commit()
        
        return redirect(url_for('historico_acessorios'))

    todos_monitores = Monitor.query.order_by(Monitor.descricao.asc()).all()
    return render_template('novo_acessorio.html', monitores=todos_monitores)

@app.route('/relatorios')
@login_required
def pagina_relatorios():
    return render_template('relatorios.html')

@app.route('/exportar/monitores')
@login_required
def exportar_monitores():
    monitores = Monitor.query.all()
    
    dados = []
    for m in monitores:
        dados.append({
            'Patrimônio': m.patrimonio,
            'Descrição': m.descricao,
            'Marca': m.marca,
            'Modelo': m.modelo,
            'S/N': m.numero_serie,
            'Local': m.local,
            'Status': m.status,
            'Empresa': m.empresa
        })
    
    df = pd.DataFrame(dados)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventário')
    
    output.seek(0)
    
    return send_file(output, 
                     download_name="inventario_monitores.xlsx", 
                     as_attachment=True)

@app.route('/exportar/preventivas')
@login_required
def exportar_preventivas():
    preventivas = Preventiva.query.all()
    dados = []
    for p in preventivas:
        dados.append({
            'Data': p.data_preventiva,
            'Mês': p.mes,
            'Equipamento': p.monitor.descricao,
            'Patrimônio': p.monitor.patrimonio,
            'Responsável': p.responsavel
        })
    
    df = pd.DataFrame(dados)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Preventivas')
    
    output.seek(0)
    return send_file(output, download_name="historico_preventivas.xlsx", as_attachment=True)


# INICIALIZAÇÃO DO SERVIDOR (Sempre no FIM)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        if not Usuario.query.first():
            senha_criptografada = generate_password_hash('123456')
            admin = Usuario(nome='Administrador', username='admin', senha=senha_criptografada)
            db.session.add(admin)
            db.session.commit()
            print("Utilizador criado! Login: admin | Senha: 123456")
            
    app.run(debug=True, use_reloader=False)