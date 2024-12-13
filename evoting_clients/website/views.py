from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import VOTER, ELECTION, OFFICE
from .forms import applyingForm, authenticateForm
from crypto.CryptoUtils.certificate import *
from crypto.key_manager import *
from adm_client import *
from reg_client import *


import json

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'authentication/register.html', {"error": "Username and password are required"})

        if VOTER.objects.filter(CPF=username).exists():
            # Cria o usuário
            user = User.objects.create_user(
                username=username,
                password=password  # O `create_user` já lida com a criptografia da senha
            )

            # Autentica e salva o usuário na sessão
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)  # Salva o usuário na sessão

                # Gera o token JWT
                refresh = RefreshToken.for_user(user)
                request.session['refresh'] = str(refresh)
                request.session['access'] = str(refresh.access_token)

                return redirect('homepage')  # Redireciona para a homepage

        else:
            return render(request, 'authentication/register.html', {"error": "User is not eligible for any election."})

    return render(request, 'authentication/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Salva o usuário na sessão

            # Gera o token JWT
            refresh = RefreshToken.for_user(user)
            request.session['refresh'] = str(refresh)
            request.session['access'] = str(refresh.access_token)

            return redirect('homepage')  # Redireciona para a homepage

        return render(request, 'authentication/login.html', {"error": "Invalid credentials"})

    return render(request, 'authentication/login.html')


def homepage(request):
    if 'access' in request.session:
        voter = VOTER.objects.filter(CPF=request.user.username).first()
        form = authenticateForm(user=request.user)
        form1 = applyingForm(user=request.user)

        if request.method == 'POST' and request.POST.get('form_type') == 'authenticate':
            electionid = request.POST.get('authenticateElection')
            password = request.POST.get('authenticatePassword')

            if request.user.check_password(password):

                voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)

                cert, enc_key, salt = authentication(voter.NAME, voter.CPF, voter.ELECTIONID.ELECTIONID, password)

                voter.PUB_KEY = cert.decode('utf-8')
                voter.PRIV_KEY = enc_key
                voter.SALT = salt
                voter.save()

                return render(request, 'home/homepage.html', {"success": "Voter authenticated successfully!", 'authenticateform': form, 'applyingform': form1, 'username':voter.NAME})
            
            else:
                return render(request, 'home/homepage.html', {"error": "Invalid credentials!", 'authenticateform': form, 'applyingform': form1, 'username':voter.NAME})

        if request.method == 'POST' and request.POST.get('form_type') == 'apply':
            electionid = request.POST.get('applyElection')
            office = request.POST.get('office')
            campaignid = request.POST.get('campaignId')
            password = request.POST.get('applyPassword')

            voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)

            if request.user.check_password(password):
                pub_key = search_public_key(voter.PUB_KEY)
                priv_key = search_private_key(password, voter.SALT, voter.PRIV_KEY)

                header, content = applying(voter.CPF, electionid, campaignid, office, priv_key, pub_key)

                return render(request, 'home/homepage.html', {header: content, 'authenticateform': form, 'applyingform': form1, 'username':voter.NAME})
            
            else:
                return render(request, 'home/homepage.html', {"error": "Invalid credentials!", 'authenticateform': form, 'applyingform': form1, 'username':voter.NAME})
        
        return render(request, 'home/homepage.html', {'authenticateform': form, 'applyingform': form1, 'username':voter.NAME})
    
    return redirect('login')
    
def load_offices(request):
    election_id = request.GET.get('election_id')
    offices = OFFICE.objects.filter(ELECTIONID=election_id)
    office_options = [(office.id, office.NAME) for office in offices]
    return JsonResponse(office_options, safe=False)

def logout(request):
    request.session.flush()  # Limpa a sessão
    return redirect('login')  # Redireciona para a página de login
