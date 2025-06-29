"""
FORMULÁRIOS DO SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Este módulo contém todos os formulários do sistema, incluindo:
- Formulário para criação/edição de agendamentos
- Validações customizadas para dados de agendamento
- Controle de estado ativo/inativo dos agendamentos

FORMULÁRIOS:
- AlarmForm: Formulário completo para manipulação de AlarmSchedule
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import AlarmSchedule


class AlarmForm(forms.ModelForm):
    """
    Formulário completo para manipulação de AlarmSchedule
    
    Campos personalizados:
    - days_of_week: Exibido como checkboxes múltiplos
    - time: Campo de horário com input type='time'
    - start_date/end_date: Campos de data com input type='date'
    - active: Sempre inicializado como True (novos registros)
    """

    days_of_week = forms.MultipleChoiceField(
        choices=AlarmSchedule.DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Dias da Semana',
        help_text='Selecione os dias de repetição'
    )

    class Meta:
        model = AlarmSchedule
        fields = ['event_type', 'time', 'days_of_week', 'start_date', 'end_date', 'active']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
	    super().__init__(*args, **kwargs)
	    if not self.instance.pk:  # Se for um novo registro
		    self.fields['active'].initial = True
		    self.fields['active'].widget = forms.HiddenInput()  # Oculta o campo
	    else:
		    self.fields['active'].disabled = True  # Bloqueia alteração para registros existentes

    def clean_days_of_week(self):
        """
        Valida e formata os dias da semana selecionados
        
        Retorna:
        - String com dias separados por vírgula (ex: "SEG,QUA,SEX")
        
        Erros:
        - ValidationError se nenhum dia for selecionado
        """
        days = self.cleaned_data.get('days_of_week', [])
        if not days:
            raise ValidationError("Selecione pelo menos um dia da semana.")
        return ",".join(days)

    def clean(self):
        """
        Validação cruzada dos campos:
        - Verifica se a data final é maior que a data inicial
        - Garante coerência temporal nos agendamentos
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError({
                'end_date': "A data final deve ser posterior à data inicial."
            })
            
        return cleaned_data