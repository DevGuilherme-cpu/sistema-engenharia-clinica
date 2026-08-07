from django import forms
from .models import Manutencao

class ManutencaoForm(forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = '__all__'
        
        widgets = {
            'data_execucao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'equipamento': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'tecnico_responsavel': forms.TextInput(attrs={'class': 'form-control'}),
            'custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'defeito_informado': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'solucao_aplicada': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }