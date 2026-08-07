from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File

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
    data_execucao = models.DateField()
    tecnico_responsavel = models.CharField(max_length=100)
    custo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    defeito_informado = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    solucao_aplicada = models.TextField(blank=True, null=True)
    pecas_utilizadas = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    
    proxima_preventiva = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.equipamento.descricao}"
    
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