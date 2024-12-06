from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import VOTER, ELECTION, OFFICE
from adm_client import *
from reg_client import *

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
    list_display = ('ELECTIONID', 'YEAR', 'NUM_OFFICES')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        print("Election ID:", obj.ELECTIONID)
        print("Year:", obj.YEAR)
        print("Number of Offices:", obj.NUM_OFFICES)
        
        electionSetting(obj.ELECTIONID, obj.NUM_OFFICES)

class OfficeAdmin(admin.ModelAdmin):
    list_display = ('NAME', 'ELECTIONID', 'DIGIT_NUM')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        print("Name:", obj.NAME)
        print("Election:", obj.ELECTIONID)
        print("Number of digits:", obj.DIGIT_NUM)
        
        officeSetting(obj.NAME, obj.ELECTIONID.ELECTIONID, obj.DIGIT_NUM)

class VoterAdmin(admin.ModelAdmin):
    list_display = ('NAME', 'CPF',
                    'ELECTIONID', 'PUB_KEY', 
                    'PRIV_KEY')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print('Cpf:', obj.CPF)
        print('Election ID:', obj.ELECTIONID)
        print('Name:', obj.NAME)
        
        registering(obj.NAME, obj.CPF, obj.ELECTIONID.ELECTIONID)
        


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ELECTION, ElectionAdmin)
admin.site.register(VOTER, VoterAdmin)
admin.site.register(OFFICE, OfficeAdmin)

