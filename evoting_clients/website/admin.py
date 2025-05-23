from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import VOTER, ELECTION, OFFICE
from .clients.adm import *
from .clients.reg import *
from .clients.tal import *
from .clients.val import *

# Register your models here.

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

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password'),
        }),
    )

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('ELECTIONID', 'END_SETTING', 'END_ELECTION')

    def save_model(self, request, obj, form, change):
        header, content = electionSetting(obj.ELECTIONID, obj.END_SETTING, obj.END_ELECTION)
        print(header, content)
        
        if header != 'error':
            super().save_model(request, obj, form, change)
        
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('NAME', 'ELECTIONID')

    def save_model(self, request, obj, form, change):
        header, content = officeSetting(obj.NAME, obj.ELECTIONID.ELECTIONID)
        
        if header != 'error':
            super().save_model(request, obj, form, change)

class VoterAdmin(admin.ModelAdmin):
    list_display = ('NAME', 'CPF',
                    'ELECTIONID', 'PUB_KEY', 
                    'PRIV_KEY', 'AUTH',
                    'CANDIDATE')
    exclude = ('PUB_KEY','PRIV_KEY','AUTH', 'CANDIDATE')
    
    def save_model(self, request, obj, form, change):
        header, content = registering(obj.NAME, obj.CPF, obj.ELECTIONID.ELECTIONID)

        if header != 'error':
            super().save_model(request, obj, form, change)
        
        
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ELECTION, ElectionAdmin)
admin.site.register(VOTER, VoterAdmin)
admin.site.register(OFFICE, OfficeAdmin)

