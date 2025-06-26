from django import forms
from .models import *

"""
FORMULÁRIO DE AGENDAMENTO DE EVENTOS – SISTEMA DE MONITORAMENTO IoT

DESCRIÇÃO:
Este módulo define o formulário utilizado para criar ou editar eventos agendados no sistema IoT.
Permite a seleção de dias da semana via checkboxes e o preenchimento de dados como tipo de evento,
horário e período de vigência. O campo `days_of_week` é tratado como múltipla escolha e convertido
em string separada por vírgulas para armazenamento no banco de dados.

FORMULÁRIOS:
- AlarmForm: formulário vinculado ao modelo AlarmSchedule, com customização no campo de dias da semana.
"""

#### FORMULÁRIO DE AGENDAMENTO DE EVENTOS ####
class AlarmForm(forms.ModelForm):
    # Campo personalizado para múltipla escolha de dias (exibido como checkboxes)
    days_of_week = forms.MultipleChoiceField(
        choices=AlarmSchedule.DAYS_CHOICES,                      # Lista de opções válidas (SEG, TER, etc.)
        widget=forms.CheckboxSelectMultiple,                     # Widget HTML: checkbox múltiplo
        label='Dias da Semana',                                  # Rótulo exibido no formulário
        help_text='Selecione um ou mais dias'                    # Texto auxiliar ao usuário
    )

    class Meta:
        model = AlarmSchedule                                    # Modelo associado ao formulário
        fields = [                                               # Campos exibidos no formulário
            'event_type',
            'time',
            'days_of_week',
            'start_date',
            'end_date',
        ]
        widgets = {                                              # Personalização dos campos (HTML5)
            'time': forms.TimeInput(attrs={'type': 'time'}),        # Campo de horário
            'start_date': forms.DateInput(attrs={'type': 'date'}),  # Campo de data inicial
            'end_date': forms.DateInput(attrs={'type': 'date'}),    # Campo de data final
        }

    def clean_days_of_week(self):
        """
        Valida e converte a lista de dias da semana selecionados
        em uma string separada por vírgulas (ex: 'SEG,QUA,SEX').

        Returns:
            str: Dias formatados como string

        Raises:
            forms.ValidationError: Se nenhum dia for selecionado
        """
        dias = self.cleaned_data.get('days_of_week', [])
        if not dias:
            raise forms.ValidationError("Selecione ao menos um dia da semana.")
        return ",".join(dias)
