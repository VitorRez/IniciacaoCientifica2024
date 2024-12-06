from django import forms
from .models import VOTER, ELECTION, OFFICE

class applyingForm(forms.Form):
    applyElection = forms.ModelChoiceField(
        queryset=ELECTION.objects.all(),
        label="Selecione a Eleição",
        empty_label="Selecione uma eleição"
    )
    office = forms.ChoiceField(
        label="Selecione o Cargo",
        choices=[],
        required=True
    )
    applyPassword = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=True
    )
    campaignId = forms.IntegerField(
        label="Número de campanha",
        widget=forms.TextInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extrai o usuário dos argumentos
        super().__init__(*args, **kwargs)

        # Filtra eleições baseadas nas eleições do usuário
        if user is not None:
            registered_elections = VOTER.objects.filter(CPF=user.username).values_list('ELECTIONID', flat=True)
            self.fields['applyElection'].queryset = ELECTION.objects.filter(ELECTIONID__in=registered_elections)

        # Inicializa `office` vazio até uma eleição ser selecionada
        self.fields['office'].choices = []

class authenticateForm(forms.Form):
    authenticateElection = forms.ModelChoiceField(
        queryset=ELECTION.objects.all(),
        label="Selecione a Eleição",
        empty_label="Selecione uma eleição"
    )
    authenticatePassword = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extrai o usuário dos argumentos
        super().__init__(*args, **kwargs)

        # Filtra eleições baseadas nas eleições do usuário
        if user is not None:
            registered_elections = VOTER.objects.filter(CPF=user.username).values_list('ELECTIONID', flat=True)
            self.fields['authenticateElection'].queryset = ELECTION.objects.filter(ELECTIONID__in=registered_elections)