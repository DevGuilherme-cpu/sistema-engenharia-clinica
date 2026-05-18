from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False) # Guardará a senha criptografada

class Monitor(db.Model):
    __tablename__ = 'monitores'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(150), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100), unique=True)
    patrimonio = db.Column(db.String(50), unique=True)
    local = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Completa') # Completa, Pendente, Manutenção, Desaparecido
    empresa = db.Column(db.String(100))
    contrato = db.Column(db.String(100))
    preventivas = db.relationship('Preventiva', backref='monitor', lazy=True)
    acessorios = db.relationship('Acessorio', backref='monitor', lazy=True)
    manutencoes = db.relationship('ManutencaoExterna', backref='monitor', lazy=True)

class Preventiva(db.Model):
    __tablename__ = 'preventivas'
    
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitores.id'), nullable=False)
    data_preventiva = db.Column(db.Date, nullable=False)
    mes = db.Column(db.String(20)) # Ex: "Janeiro", "Fevereiro"
    responsavel = db.Column(db.String(100))

class Acessorio(db.Model):
    __tablename__ = 'acessorios'
    
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitores.id'), nullable=False)
    tipo = db.Column(db.String(100), nullable=False) # Ex: Braçadeira, ECG, Oxímetro
    data_troca = db.Column(db.Date)

class ManutencaoExterna(db.Model):
    __tablename__ = 'manutencao_externa'
    
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitores.id'), nullable=False)
    motivo = db.Column(db.String(255), nullable=False) # Ex: Tela Quebrada, Troca de Bateria
    empresa = db.Column(db.String(100), nullable=False) # Empresa que levou
    data_saida = db.Column(db.Date, nullable=False)
    previsao_retorno = db.Column(db.Date)
    data_retorno = db.Column(db.Date) 
    tecnico = db.Column(db.String(100)) 
    status = db.Column(db.String(50), default='Aguardando Retorno')