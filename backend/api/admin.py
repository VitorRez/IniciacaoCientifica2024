from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .adminForm import CustomUserCreationForm
from .models import Voter, Election, Offices
from .clients.crypto.ciphers import *
from .clients.crypto.PBKDF import *
from .clients.election_client import *
from .clients.reg_client import *

# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password'),
        }),
    )

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('electionid', 'year', 'num_offices')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print("Election ID:", obj.electionid)
        print("Year:", obj.year)
        print("Number of Offices:", obj.num_offices)
        msg = '0' + ' ' + str(obj.electionid) + ' ' + str(obj.num_offices)
        print(msg)
        send_to_server(msg)

class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'electionid', 'digit_num')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print("Name:", obj.name)
        print("Election:", obj.electionid.electionid)
        print("Number of digits:", obj.digit_num)
        msg = '1' + ' ' + obj.name + ' ' + str(obj.electionid.electionid) + ' ' + str(obj.digit_num)
        print(msg)
        send_to_server(msg)

class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'voterid',
                    'electionid', 'auth',
                    'pub_key', 'priv_key',
                    'nonce', 'hash', 'salt')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print('Cpf:', obj.voterid)
        print('Election:', obj.electionid.electionid)
        print('Name:', obj.name)
        msg = '0 ' + obj.name + ' ' + str(obj.voterid) + ' ' + str(obj.electionid.electionid)
        print(msg)
        registration(msg)
        


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(Offices, OfficeAdmin)

