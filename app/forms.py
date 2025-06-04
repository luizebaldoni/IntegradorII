# app/forms.py
from django import forms
from .models import AlarmSchedule

class AlarmForm(forms.ModelForm):
    # Sobrescreve days_of_week como múltipla escolha (checkboxes)
    days_of_week = forms.MultipleChoiceField(
        choices=AlarmSchedule.DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Dias da Semana',
        help_text='Selecione um ou mais dias'
    )

    class Meta:
        model = AlarmSchedule
        fields = [
            'event_type',
            'time',
            'days_of_week',
            'start_date',
            'end_date',
        ]
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_days_of_week(self):
        """
        Recebe a lista de valores (ex: ['SEG', 'QUA', 'SEX'])
        e converte para string “MON,WED,FRI” para armazenar no model.
        """
        dias = self.cleaned_data.get('days_of_week', [])
        # Garante que seja uma lista de strings válidas
        if not dias:
            raise forms.ValidationError("Selecione ao menos um dia da semana.")
        return ",".join(dias)
