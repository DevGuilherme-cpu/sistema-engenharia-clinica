from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone

# Tabela dos Setores
class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Setor")
    sigla = models.CharField(max_length=100, blank=True, unique=True, verbose_name="Sigla (Opicional)")

    def __str__(self):
        if self.sigla:
            return f"{self.sigla} - {self.nome}"
        return self.nome
    
    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ['nome']

# Tabela dos Equipamentos
class Equipamento(models.Model):
    STATUS_CHOICES = [
        ('funcionamento', 'Em funcionamento'),
        ('manutencao', 'Em manutenção'),
        ('interditado', 'Interditado'),
        ('nao_localizado', 'Não localizado'),
    ]

    patrimonio = models.CharField(max_length=50, unique=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    registro_anvisa = models.CharField(max_length=100, blank=True, null=True)
    
    descricao = models.CharField(max_length=200) # Ex: Monitor Multiparamétrico
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipamentos')
    localizacao_detalhada = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localização Detalhada")
    
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    data_aquisicao = models.DateField(blank=True, null=True)
    valor_aquisicao = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vida_util_anos = models.IntegerField(blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='funcionamento')
    observacoes = models.TextField(blank=True, null=True)
    
    # Arquivos (Fotos, Manuais e QR Code automático)
    foto = models.ImageField(upload_to='equipamentos/fotos/', blank=True, null=True)
    manual_tecnico = models.FileField(upload_to='equipamentos/manuais/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='equipamentos/qr_codes/', blank=True, null=True)

    def __str__(self):
        return f"{self.descricao} - {self.patrimonio}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if not self.qr_code:
            link = f"http://127.0.0.1:8000/equipamentos/visualizar/{self.id}/"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            nome_arquivo = f'qr_equip_{self.patrimonio}.png'
            self.qr_code.save(nome_arquivo, File(buffer), save=False)
            
            super().save(update_fields=['qr_code'])

# Tabela de Manutenções
class Manutencao(models.Model):
    TIPO_CHOICES = [
        ('preventiva', 'Preventiva'),
        ('corretiva', 'Corretiva'),
    ]

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='manutencoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    tipo_manutencao = models.CharField(max_length=50)
    data_execucao = models.DateField()
    tecnico = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='Concluída')
    titulo = models.CharField(max_length=200, null=True, blank=True)
    descricao = models.CharField(null=True, blank=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_registro = models.DateTimeField(auto_now_add=True)
    
    defeito_informado = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    solucao_aplicada = models.TextField(blank=True, null=True)
    pecas_utilizadas = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    proxima_preventiva = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_manutencao} - {self.equipamento.patrimonio}"
    
# Tabela de Oficina externa
class OficinaExterna(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='envios_oficina')
    empresa = models.CharField(max_length=100)
    data_envio = models.DateField()
    data_retorno = models.DateField(blank=True, null=True)
    ordem_servico = models.CharField(max_length=50, blank=True, null=True)
    valor_orcamento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.empresa} - {self.equipamento.descricao}"
    
class TrocaAcessorio(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    nome_acessorio = models.CharField(max_length=100)
    data_troca = models.DateField()
    motivo = models.CharField(max_length=200)
    tecnico = models.CharField(max_length=100)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Troca: {self.nome_acessorio} - {self.equipamento.patrimonio}"
    
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='perfil/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
# --- GUIA DE MOVIMENTAÇÃO (GMBP) ---
class GuiaMovimentacao(models.Model):
    ESTADO_CONSERVACAO_CHOICES = [
        ('RUIM', 'Ruim'),
        ('INTERMEDIARIO', 'Intermediário'),
        ('PERFEITO', 'Perfeito'),
    ]

    TIPO_MOVIMENTACAO_CHOICES = [
        ('TRANSFERENCIA_INTERNA', 'Transferência Interna'),
        ('TRANSFERENCIA_EXTERNA', 'Transferência Externa'),
        ('EMPRESTIMO_INTERNO', 'Empréstimo Interno'),
        ('EMPRESTIMO_EXTERNO', 'Empréstimo Externo'),
        ('DEVOLUCAO', 'Devolução'),
    ]

    # Relação com o Equipamento
    equipamento = models.ForeignKey('Equipamento', on_delete=models.CASCADE, related_name='guias_movimentacao')
    numero_guia = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: GMBP-01-2026")
    
    orgao_cedente = models.CharField(max_length=255, default="SECRETARIA ESTADUAL DE SAUDE DO TOCANTINS")
    unidade_cedente = models.CharField(max_length=255, default="GERENCIA DE ENGENHARIA CLINICA - SES")
    municipio_cedente = models.CharField(max_length=100, default="Palmas")
    
    orgao_receptor = models.CharField(max_length=255, default="SECRETARIA ESTADUAL DE SAUDE DO TOCANTINS")
    unidade_receptor = models.CharField(max_length=255, help_text="Ex: ENGENHARIA CLINICA - HGP")
    municipio_receptor = models.CharField(max_length=100, default="Palmas")
    
    tipo_movimentacao = models.CharField(max_length=50, choices=TIPO_MOVIMENTACAO_CHOICES)
    data_emissao = models.DateTimeField(default=timezone.now)
    
    estado_conservacao = models.CharField(max_length=20, choices=ESTADO_CONSERVACAO_CHOICES, default='PERFEITO')
    quantidade = models.IntegerField(default=1)
    valor = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    descricao_editada = models.TextField(help_text="Descrição que vai aparecer na impressão")
    patrimonio_editado = models.CharField(max_length=100)
    numero_serie_editado = models.CharField(max_length=100, blank=True)
    
    responsavel_cedente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guias_emitidas')
    responsavel_receptor_nome = models.CharField(max_length=255, blank=True, help_text="Nome de quem recebeu")

    def __str__(self):
        return f"GMBP - {self.equipamento} ({self.data_emissao.strftime('%d/%m/%Y')})"


# --- TERMO DE ENTREGA ---
class TermoEntrega(models.Model):
    equipamento = models.ForeignKey('Equipamento', on_delete=models.CASCADE, related_name='termos_entrega')
    ordem_impressao = models.IntegerField(default=1, help_text="Nº da Ordem na folha (ex: 01)")
    
    setor_destino = models.CharField(max_length=255, help_text="Ex: COORDENAÇÃO DO CENTRO CIRURGICO")
    data_entrega = models.DateField(default=timezone.now)
    
    acessorios_inclusos = models.TextField(help_text="O que vai junto com o equipamento")
    acessorios_pendentes = models.TextField(blank=True, help_text="Atenção: O que será entregue depois")
    
    descricao_editada = models.CharField(max_length=255, help_text="Ex: MONITOR LIFEMED – M12")
    patrimonio_editado = models.CharField(max_length=100)

    responsavel_entrega = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='termos_entregues')
    responsavel_recebimento_nome = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Termo de Entrega - {self.equipamento} ({self.setor_destino})"