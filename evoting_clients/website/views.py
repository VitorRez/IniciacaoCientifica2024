from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from .models import VOTER, ELECTION, OFFICE
from .forms import applyingForm, authenticateForm, commitForm
from .crypto.CryptoUtils.certificate import *
from .crypto.key_manager import *
from .clients.adm import *
from .clients.reg import *
from .clients.tal import *
from .clients.val import *
from datetime import datetime, timedelta
from pytz import timezone
from itertools import groupby
import json

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = create_hash(request.POST.get('password'))

        if not username or not password:
            return render(request, 'authentication/register.html', {"error": "Username and password are required"})
        
        response = get_voters_by_cpf(username)

        if response['success']:
            voter = response['data'][0]
            response = create_user(name, username, password)

            refresh = RefreshToken()
            refresh.payload["username"] = username
            refresh.set_exp(from_time=now(), lifetime=timedelta(days=1)) 

            request.session['refresh'] = str(refresh)
            request.session['access'] = str(refresh.access_token)
            request.session['user'] = username

            return redirect('homepage')

        else:
            return render(request, 'authentication/register.html', {"error": "User is not eligible for any election."})

    return render(request, 'authentication/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        response = get_user(username)

        if response['success'] and verify_hash(password, response['data']['password']):
            user = response['data']

            refresh = RefreshToken()
            refresh.payload["username"] = username
            refresh.set_exp(from_time=now(), lifetime=timedelta(days=1)) 

            request.session['refresh'] = str(refresh)
            request.session['access'] = str(refresh.access_token)
            request.session['user'] = username

            return redirect('homepage')
        

        return render(request, 'authentication/login.html', {"error": "Invalid credentials"})

    return render(request, 'authentication/login.html')


def homepage(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])

            if is_staff(request.session['user']):
                user = get_user(request.session['user'])['data']
                name = user['name']
                cpf = user['username']

                response = get_elections()

                if response["success"]:
                    return render(request, 'admin/homepage.html', {'page': 'Homepage', 'username': name, 'cpf': cpf, 'cards': response["data"]})

            else:
                user = get_user(request.session['user'])['data']
                voters = get_voters_by_cpf(request.session['user'])['data']
                
                name = voters[0]['name']
                cpf = voters[0]['cpf']

                cards = [{
                        'electionid': voter['electionid'],
                        'description': voter['description'],
                        'end_setting': voter['end_setting'],
                        'end_election': voter['end_election'],
                        'auth': voter['auth'],
                        'candidate': voter['candidate'],
                    }
                    for voter in voters
                ]

                return render(request, 'home/homepage.html', {'username':name, 'cpf':cpf, 'cards':cards})
                    
        except (TokenError, InvalidToken):
            return redirect('login')

    return redirect('login')

def create_elections(request):
    if 'access' in request.session and is_staff(request.session['user']):
        
        try:
            access_token = AccessToken(request.session['access'])

            user = get_user(request.session['user'])['data']
            name = user['name']
            cpf = user['username']
            elections = get_elections()["data"]
            
            if request.method == 'POST':
                if 'electionid' in request.POST:
                    electionid = request.POST.get('electionid')
                    response = delete_election(electionid)

                    elections = get_elections()["data"]

                    if response['success']:
                        return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections, 'error': response['error']})

                else:
                    end_setting = request.POST.get('end_setting')
                    end_election = request.POST.get('end_election')
                    description = request.POST.get('description')

                    try:
                        end_setting = datetime.fromisoformat(end_setting)
                        end_election = datetime.fromisoformat(end_election)

                    except ValueError:
                        return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections, 'error': ValueError})

                    response = create_election(end_setting, end_election, description)

                    elections = get_elections()["data"]
                    
                    if response['success']:
                        return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections, 'error': response['error']})


            return render(request, 'admin/create_elections.html', {'page': 'Elections', 'username':name, 'cpf':cpf, 'elections': elections})

        except:
                return redirect('login')
        
    else:
        return redirect('login')
        

def create_voters(request):
    if 'access' in request.session and is_staff(request.session['user']):
        try:
            access_token = AccessToken(request.session['access'])

            user = get_user(request.session['user'])['data']
            name = user['name']
            cpf = user['username']
            elections = get_elections()["data"]
            voters = get_voters()["data"]

            if request.method == 'POST':
                if 'delete_cpf' in request.POST:
                    delete_electionid, delete_cpf = request.POST.get('delete_cpf').split()
                    
                    response = delete_voter(delete_cpf, delete_electionid)

                    voters = get_voters()["data"]

                    if response['success']:
                        return render(request, 'admin/create_voters.html', {'page': 'Voters', 'username': name, 'cpf': cpf, 'elections': elections, 'voters': voters, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_voters.html', {'page': 'Voters', 'username': name, 'cpf': cpf, 'elections': elections, 'voters': voters, 'error': response["error"]})


                else:
                    voter_name = request.POST.get('name')
                    voter_cpf = request.POST.get('cpf')
                    electionid = request.POST.get('electionid')

                    response = create_voter(voter_name, voter_cpf, electionid)
                    print(response)
                    
                    voters = get_voters()["data"]

                    if response['success']:
                        return render(request, 'admin/create_voters.html', {'page': 'Voters', 'username': name, 'cpf': cpf, 'elections': elections, 'voters': voters, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_voters.html', {'page': 'Voters', 'username': name, 'cpf': cpf, 'elections': elections, 'voters': voters, 'error': response["error"]})


            return render(request, 'admin/create_voters.html', {'page': 'Voters', 'username': name, 'cpf': cpf, 'elections': elections, 'voters': voters})
        
        except:
                return redirect('login')
        
    else:
        return redirect('login')
    
def voter(request):
    if 'access' in request.session and request.user.is_staff:
        try:
            access_token = AccessToken(request.session['access'])
            electionid = request.GET.get('electionid') or request.POST.get('electionid')
            cpf = request.GET.get('cpf') or request.POST.get('cpf')

            

        except:
            return redirect('login')
        
    else:
        return redirect('login')

def create_offices(request):
    if 'access' in request.session and is_staff(request.session['user']):
        
        try:
            access_token = AccessToken(request.session['access'])

            user = get_user(request.session['user'])['data']
            name = user['name']
            cpf = user['username']
            elections = get_elections()["data"]
            offices = get_offices()["data"]

            if request.method == 'POST':
                if 'delete_office' in request.POST:
                    delete_election, delete_name = request.POST.get('delete_office').split()

                    response = delete_office(delete_name, delete_election)

                    offices = get_offices()["data"]

                    if response['success']:
                        return render(request, 'admin/create_offices.html', {'page': 'Offices', 'username': name, 'cpf': cpf, 'elections': elections, 'offices': offices, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_offices.html', {'page': 'Offices', 'username': name, 'cpf': cpf, 'elections': elections, 'offices': offices, 'error': response['error']})
            
                else:
                    office_name = request.POST.get('office_name')
                    electionid = request.POST.get('electionid')

                    response = create_office(office_name, electionid)

                    offices = get_offices()["data"]

                    if response['success']:
                        return render(request, 'admin/create_offices.html', {'page': 'Offices', 'username': name, 'cpf': cpf, 'elections': elections, 'offices': offices, 'message': response['message']})
                    else:
                        return render(request, 'admin/create_offices.html', {'page': 'Offices', 'username': name, 'cpf': cpf, 'elections': elections, 'offices': offices, 'error': response['error']})

            return render(request, 'admin/create_offices.html', {'page': 'Offices', 'username': name, 'cpf': cpf, 'elections': elections, 'offices': offices})
     
        except (TokenError, InvalidToken):
            return redirect('login')
        
    return redirect('login')

def voting_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])

            voters = VOTER.objects.filter(CPF=request.user.username)

            current_time = datetime.now(timezone('America/Sao_Paulo'))
            name = voters.first().NAME
            cpf = request.user.username

            elections = []
            for voter in voters:
                elections.append(voter.ELECTIONID.ELECTIONID)
                #if current_time > voter.ELECTIONID.END_SETTING and voter.AUTH == 1 and current_time < voter.ELECTIONID.END_ELECTION:
                #    elections.append(voter.ELECTIONID.ELECTIONID)

            data = [get_candidates(election) for election in elections]
            election_data = [item for sublist in data for item in sublist]

            grouped_data = {}
            for electionid, items in groupby(sorted(election_data, key=lambda x: x['electionid']), key=lambda x: x['electionid']):
                office_group = {}
                for item in items:
                    office_name = item['office_name']
                    if office_name not in office_group:
                        office_group[office_name] = []
                    office_group[office_name].append(item)
                grouped_data[electionid] = office_group     

            if request.method == 'POST':
                for key, value in request.POST.items():
                    if key.startswith("vote-"):
                        _, electionid, office_name = key.split('-')
                        campaignid = value
                        print(f"Election ID: {electionid}, CPF: {cpf}, Office Name: {office_name}, Campaign ID: {campaignid}")

            return render(request, 'home/voting_page.html', {'username': name, 'cpf': cpf, 'elections': grouped_data})
        
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

                current_time = datetime.now(timezone('America/Sao_Paulo'))
                election = ELECTION.objects.filter(ELECTIONID=electionid).first()

                if request.user.check_password(password):
                    if election.END_SETTING < current_time:
                        voter = VOTER.objects.get(CPF=request.user.username, ELECTIONID=electionid)
                        pub_key = search_public_key(voter.PUB_KEY)
                        priv_key = search_private_key(password, voter.SALT, voter.PRIV_KEY)

                        header, commits = get_commits(pub_key, priv_key, electionid)

                        return render(request, 'home/commits.html', {'username': voter.NAME, 'cpf': request.user.username, 'electionid': electionid, 'commitform': form, 'commits': commits})
                    
                    return render(request, 'home/commits.html', {'error': 'Commit values not available now.', 'username': voter.NAME, 'cpf': request.user.username, 'commitform': form})

                return render(request, 'home/commits.html', {'error': 'Invalid credentials.', 'username': voter.NAME, 'cpf': request.user.username, 'commitform': form})

            return render(request, 'home/commits.html', {'username': voter.NAME, 'cpf': request.user.username, 'commitform': form})
        
        except (TokenError, InvalidToken):
            return redirect('login')
    
    return redirect('login')                    


def authentication_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])
            user = get_user(request.session['user'])['data']

            cpf = user['username']
            name = user['name']

            voters = get_voters_by_cpf(cpf)['data']
            elections = [{'electionid': item['electionid'], 'description': item['description']} for item in voters]

            if request.method == 'POST':
                electionid = request.POST.get('electionid')
                password = request.POST.get('password')
                print(electionid, password)


                if verify_hash(password, user['password']):

                    voter = get_voter(cpf, electionid)['data'][0]
                    print(voter)

                    if voter['auth'] == 1:
                        return render(request, 'home/authenticate.html', {"error": "voter already authenticated", "cpf": cpf, "username": name, "elections": elections})

                    response = authentication(name, cpf, voter['electionid'], password)

                    if response['success']:
                        return render(request, 'home/authenticate.html', {"success": response['message'], "cpf": cpf, "username": name, "elections": elections})
                    
                    else:
                        return render(request, 'home/authenticate.html', {"error": response['error'], "cpf": cpf, "username": name, "elections": elections})
                    
                return render(request, 'home/authenticate.html', {"error": "wrong password", "cpf": cpf, "username": name, "elections": elections})
            
            return render(request, 'home/authenticate.html', {"cpf": cpf, "username": name, "elections": elections})

        except (TokenError, InvalidToken):
            return redirect('login') 
        
        except Exception as e:
            return redirect('login')
   
    return redirect('login')
     

def applying_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])
            user = get_user(request.session['user'])['data']

            cpf = user['username']
            name = user['name']

            voters = get_voters_by_cpf(cpf)['data']
            elections = [{'electionid': item['electionid'], 'description': item['description']} for item in voters]
            offices = []

            for election in elections:
                office_by_election = get_offices_by_election(election['electionid'])['error']
                for office in office_by_election:
                    offices.append({'electionid': election['electionid'], 'office_name': office})
                
            print(offices)

            return render(request, 'home/apply.html', {
                "cpf": cpf,
                "username": name,
                "elections": elections,
                "offices": offices
            })
        
        except Exception as e:
            return redirect('login')
        
    return redirect('login')


def election_page(request):
    if 'access' in request.session:
        try:
            access_token = AccessToken(request.session['access'])
            electionid = request.GET.get('electionid') or request.POST.get('electionid')

            if is_staff(request.session['user']):
                user = get_user(request.session['user'])['data']
                name = user['name']
                cpf = user['username']

                elections = get_elections()['data']
                election = next((e for e in elections if e['electionid'] == electionid), None)
                description = election['description']

                if request.method == 'POST':
                    end_setting = request.POST.get('end_setting')
                    end_election = request.POST.get('end_election')
                    description = request.POST.get('description')

                    print(end_setting, end_election, description)

                    end_setting = datetime.fromisoformat(end_setting)
                    end_election = datetime.fromisoformat(end_election)

                    response = update_election(electionid, end_setting, end_election, description)

                    elections = get_elections()['data']
                    election = next((e for e in elections if e['electionid'] == electionid), None)
                    description = election['description']

                    if response['success']:
                        return render(request, 'admin/election.html', {
                            'page': f"Election: {description}",
                            'electionid': election["electionid"],
                            'username': name, 
                            'cpf': cpf, 
                            'election': election,
                            'message': response['message']
                        })
                    
                    else:
                        print(response['error'])
                        return render(request, 'admin/election.html', {
                            'page': f"Election: {description}",
                            'electionid': election["electionid"],
                            'username': name, 
                            'cpf': cpf, 
                            'election': election,
                            'error': response['error']
                        })
                
                return render(request, 'admin/election.html', {
                    'page': f"Election: {description}",
                    'electionid': election["electionid"],
                    'username': name, 
                    'cpf': cpf, 
                    'election': election,
                })

            voter = VOTER.objects.filter(CPF=request.user.username, ELECTIONID=electionid).first()
            name = voter.NAME
            auth = voter.AUTH
            candidate = voter.CANDIDATE
            cpf = voter.CPF

            election = ELECTION.objects.filter(ELECTIONID=electionid).first()
            end_setting = election.END_SETTING
            end_election = election.END_ELECTION

            data = get_candidates(electionid)
            print(data)

            offices = {}
            for item in data:
                office_name = item['office_name']
                if office_name not in offices:
                    offices[office_name] = []
                offices[office_name].append({
                    'name': item['name'],
                    'campaignid': item['campaignid']
                })

            return render(request, 'home/election.html', {
                'username': name, 
                'cpf': cpf, 
                'electionid': electionid,
                'offices': offices,
                'auth': auth,
                'candidate': candidate,
                'end_setting': end_setting,
                'end_election': end_election,
            })

        except (TokenError, InvalidToken):
            return redirect('login')
        
    return redirect('login')

def voting_submit(request):
    if 'access' in request.session:
        if request.method == 'POST':
            electionid = request.POST.get('electionid')
            cpf = request.user.username
            votes = {}

            for key, value in request.POST.items():
                if key.startswith('office-'):
                    office_name = key.replace('office-', '')
                    votes[office_name] = value 

            print(f"Eleição: {electionid}, CPF: {cpf}, Votos: {votes}")


            return redirect('voting')

    return redirect('login')
   
    
def load_offices(request):
    election_id = request.GET.get('election_id')
    offices = OFFICE.objects.filter(ELECTIONID=election_id)
    office_options = [(office.id, office.NAME) for office in offices]
    return JsonResponse(office_options, safe=False)

def logout(request):
    request.session.flush()  # Limpa a sessão
    return redirect('login')  # Redireciona para a página de login

        
