from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from .models import VOTER, ELECTION, OFFICE
from .forms import applyingForm, authenticateForm, commitForm
from crypto.CryptoUtils.certificate import *
from crypto.key_manager import *
from adm_client import *
from reg_client import *
from tal_client import *
import json

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'authentication/register.html', {"error": "Username and password are required"})

        if VOTER.objects.filter(CPF=username).exists():
            user = User.objects.create_user(
                username=username,
                password=password  
            )

            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)

                refresh = RefreshToken.for_user(user)
                request.session['refresh'] = str(refresh)
                request.session['access'] = str(refresh.access_token)

                return redirect('homepage')

        else:
            return render(request, 'authentication/register.html', {"error": "User is not eligible for any election."})

    return render(request, 'authentication/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            refresh = RefreshToken.for_user(user)
            request.session['refresh'] = str(refresh)
            request.session['access'] = str(refresh.access_token)

            return redirect('homepage')  # Redireciona para a homepage

        return render(request, 'authentication/login.html', {"error": "Invalid credentials"})

    return render(request, 'authentication/login.html')


def homepage(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])

            voters = VOTER.objects.filter(CPF=request.user.username)
            name, cpf = voters.first().NAME, voters.first().CPF
            cards = [{
                    'electionid': voter.ELECTIONID.ELECTIONID,
                    'end_setting': voter.ELECTIONID.END_SETTING,
                    'auth': voter.AUTH,
                    'candidate': voter.CANDIDATE,
                }

                for voter in voters
            ]
            print(cards)

            return render(request, 'home/homepage.html', {'username':name, 'cpf':cpf, 'cards':cards})
        
        except (TokenError, InvalidToken):
            return redirect('login')
    
    return redirect('login')


def commit_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])

            voter = VOTER.objects.filter(CPF=request.user.username).first()
            
            form = commitForm(user=request.user)

            if request.method == 'POST':
                electionid = request.POST.get('commitElection')
                password = request.POST.get('commitPassword')

                if request.user.check_password(password):
                    voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)
                    pub_key = search_public_key(voter.PUB_KEY)
                    priv_key = search_private_key(password, voter.SALT, voter.PRIV_KEY)

                    header, commits = get_commits(pub_key, priv_key, electionid)

                    return render(request, 'home/commits.html', {'username': voter.NAME, 'cpf': request.user.username, 'electionid': electionid, 'commitform': form, 'commits': commits})

                return render(request, 'home/commits.html', {'error': 'Invalid credentials.', 'username': voter.NAME, 'cpf': request.user.username, 'commitform': form})

            return render(request, 'home/commits.html', {'username': voter.NAME, 'cpf': request.user.username, 'commitform': form})
        
        except (TokenError, InvalidToken):
            return redirect('login')
    
    return redirect('login')

def authentication_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])

            voter = VOTER.objects.filter(CPF=request.user.username).first()

            form = authenticateForm(user=request.user)

            if request.method == 'POST':
                electionid = request.POST.get('authenticateElection')
                password = request.POST.get('authenticatePassword')

                if request.user.check_password(password):

                    voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)

                    if voter.AUTH == 1:
                        return render(request, 'home/authenticate.html', {"error": "voter already authenticated", "authenticateform": form, "cpf": voter.CPF, "username":voter.NAME})

                    data = authentication(voter.NAME, voter.CPF, voter.ELECTIONID.ELECTIONID, password)

                    if data[0] == 'success':
                        cert, enc_key, salt = data[1], data[2], data[3]

                        voter.PUB_KEY = cert.decode('utf-8')
                        voter.PRIV_KEY = enc_key
                        voter.SALT = salt
                        voter.AUTH = 1
                        voter.save()

                        return render(request, 'home/authenticate.html', {"success": "Voter authenticated successfully!", "authenticateform": form, "cpf": voter.CPF, "username":voter.NAME})
                    
                    else:
                        return render(request, 'home/authenticate.html', {"error": data[1], "authenticateform": form, "cpf": voter.CPF, "username":voter.NAME})
                    
                else:
                    return render(request, 'home/authenticate.html', {"error": data[1], "authenticateform": form, "cpf": voter.CPF, "username":voter.NAME})
                
            return render(request, 'home/authenticate.html', {"authenticateform": form, "cpf": voter.CPF, "username":voter.NAME})

        except (TokenError, InvalidToken):
            return redirect('login') 
   
    return redirect('login')

def applying_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])
            
            voter = VOTER.objects.filter(CPF=request.user.username).first()
            form = applyingForm(user=request.user)

            if request.method == 'POST':
                electionid = request.POST.get('applyElection')
                office = request.POST.get('office')
                campaignid = request.POST.get('campaignId')
                password = request.POST.get('applyPassword')

                voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)

                if request.user.check_password(password):
                    pub_key = search_public_key(voter.PUB_KEY)
                    priv_key = search_private_key(password, voter.SALT, voter.PRIV_KEY)

                    header, content = applying(voter.CPF, electionid, campaignid, office, priv_key, pub_key)

                    voter.CANDIDATE = 1
                    voter.save()

                    return render(request, 'home/apply.html', {header: content, 'applyingform': form, 'username': voter.NAME, 'cpf': voter.CPF})
                
                else:
                    return render(request, 'home/apply.html', {'error': 'Invalid credentials!', 'applyingform': form, 'username': voter.NAME, 'cpf': voter.CPF})
            
            return render(request, 'home/apply.html', {'applyingform': form, 'username': voter.NAME, 'cpf': voter.CPF})
        
        except (TokenError, InvalidToken):
            return redirect('login')
        
    return redirect('login')
   
    
def load_offices(request):
    election_id = request.GET.get('election_id')
    offices = OFFICE.objects.filter(ELECTIONID=election_id)
    office_options = [(office.id, office.NAME) for office in offices]
    return JsonResponse(office_options, safe=False)

def logout(request):
    request.session.flush()  # Limpa a sessão
    return redirect('login')  # Redireciona para a página de login

        
