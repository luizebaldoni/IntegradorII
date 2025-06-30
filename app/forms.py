"""
FORMULÁRIOS DO SISTEMA DE SIRENE ESCOLAR

DESCRIÇÃO:
Este módulo define os formulários utilizados na interface web do sistema, com foco no gerenciamento
de agendamentos de sirene (modelo AlarmSchedule). Inclui campos customizados, validações específicas
e lógica de exibição conforme o contexto (criação vs. edição).

FORMULÁRIOS DEFINIDOS:
- AlarmForm: Criação e edição de alarmes semanais com campos personalizados.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import AlarmSchedule

# ========================================================
# FORMULÁRIO PARA CADASTRO E EDIÇÃO DE AGENDAMENTOS
# ========================================================

class AlarmForm(forms.ModelForm):
    """
    Formulário completo para criar ou editar agendamentos de sirene (AlarmSchedule).

    Personalizações:
    - 'days_of_week' como múltipla escolha com checkboxes
    - Campos 'time', 'start_date', 'end_date' com widgets de HTML5 (time/date)
    - Campo 'active' é ocultado na criação e bloqueado na edição
    """

    # Campo personalizado com múltipla escolha e checkboxes
    days_of_week = forms.MultipleChoiceField(
        choices=AlarmSchedule.DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Dias da Semana',
        help_text='Selecione os dias em que o alarme será ativado'
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
        """Ajusta o comportamento do campo 'active' de acordo com o contexto"""
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Oculta o campo ao criar novo agendamento
            self.fields['active'].initial = True
            self.fields['active'].widget = forms.HiddenInput()
        else:
            # Bloqueia edição para registros já existentes
            self.fields['active'].disabled = True

    def clean_days_of_week(self):
        """
        Valida o campo 'days_of_week':
        - Garante que ao menos um dia seja selecionado
        - Converte lista para string separada por vírgulas
        """
        days = self.cleaned_data.get('days_of_week', [])
        if not days:
            raise ValidationError("Selecione pelo menos um dia da semana.")
        return ",".join(days)

    def clean(self):
        """
        Validação cruzada entre campos:
        - Garante que 'end_date' seja posterior a 'start_date'
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError({
                'end_date': "A data final deve ser posterior à data inicial."
            })

        return cleaned_data
