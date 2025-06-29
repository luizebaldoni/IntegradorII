"""
FORMULÁRIOS DO SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Este módulo contém todos os formulários do sistema, incluindo:
- Formulário para criação/edição de agendamentos
- Validações customizadas para dados de agendamento

FORMULÁRIOS:
- AlarmForm: Formulário para manipulação de AlarmSchedule
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import AlarmSchedule


class AlarmForm(forms.ModelForm):
	"""
    Formulário para criação/edição de agendamentos

    Campos personalizados:
    - days_of_week: Exibido como checkboxes múltiplos
    - time: Campo de horário com input type='time'
    - start_date/end_date: Campos de data com input type='date'
    """
	days_of_week = forms.MultipleChoiceField(
			choices = AlarmSchedule.DAYS_CHOICES,
			widget = forms.CheckboxSelectMultiple,
			label = 'Dias da Semana',
			help_text = 'Selecione os dias de repetição'
			)
	
	class Meta:
		model = AlarmSchedule
		fields = ['event_type', 'time', 'days_of_week', 'start_date', 'end_date', 'active']
		widgets = {
				'time': forms.TimeInput(attrs = {'type': 'time'}),
				'start_date': forms.DateInput(attrs = {'type': 'date'}),
				'end_date': forms.DateInput(attrs = {'type': 'date'}),
				}
		labels = {
				'active': 'Ativo'
				}
	
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
        Validação cruzada dos campos
        - Verifica se a data final é maior que a data inicial
        """
		cleaned_data = super().clean()
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date and end_date and end_date < start_date:
			raise ValidationError("A data final deve ser posterior à data inicial.")
		
		return cleaned_data