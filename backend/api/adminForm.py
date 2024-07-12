from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        print("Creating a new user with the following details:")

        print(self.cleaned_data['username'])
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user