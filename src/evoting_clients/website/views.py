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
    if request.method != 'POST':
        return render(request, 'authentication/register.html')

    username = request.POST.get('username')
    password = create_hash(request.POST.get('password'))
    
    response = get_voters_by_cpf(username)

    if not response['success']:
        return render(request, 'authentication/register.html',{
            "error": "User is not eligible for any available election."
        })
    
    voter = response['data'][0]
    response = create_user(voter['name'], username, password)

    refresh = RefreshToken()
    refresh.payload["username"] = username
    refresh.set_exp(from_time=now(), lifetime=timedelta(days=1)) 

    request.session['refresh'] = str(refresh)
    request.session['access'] = str(refresh.access_token)
    request.session['user'] = username

    return redirect('homepage')


def login_view(request):
    if request.method != 'POST':
        return render(request, 'authentication/login.html')
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    response = get_user(username)
    
    if not response['success']:
        return render(request, 'authentication/login.html', {
            "error": "User not found."
        })
    
    user = response['data']
    
    if not verify_hash(password, user['password']):
        return render(request, 'authentication/login.html', {
            "error": "Invalid password."
        })

    refresh = RefreshToken()
    refresh.payload["username"] = username
    refresh.set_exp(from_time=now(), lifetime=timedelta(days=1)) 

    request.session['refresh'] = str(refresh)
    request.session['access'] = str(refresh.access_token)
    request.session['user'] = username

    return redirect('homepage')


def homepage(request):
    if 'access' not in request.session:
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        if is_staff(cpf):
            elections = get_elections()['data']

            return render(request, 'admin/homepage.html', {
                "page": "Homepage",
                "user": user,
                "cards": elections
            })
        
        else:
            cards = get_voters_by_cpf(cpf)['data']

            return render(request, 'home/homepage.html', {
                "page": "Homepage",
                "user": user,
                "cards": cards
            }) 

    except (TokenError, InvalidToken):
        return redirect('login')


def create_elections(request):
    if 'access' not in request.session:
        redirect('login')

    if not is_staff(request.session['user']):
        redirect('login')

    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_elections()['data']

        if request.method != 'POST':
            return render(request, 'admin/create_elections.html', {
                "page": "Elections",
                "user": user,
                "elections": elections
            })

        if 'electionid' in request.POST:
            electionid = request.POST.get('electionid')
            response = delete_election(electionid)

            elections = get_elections()['data']

            if response['success']:
                return render(request, 'admin/create_elections.html', {
                    "page": "Elections",
                    "message": response['message'], 
                    "user": user,
                    "elections": elections
                })
            else:
                return render(request, 'admin/create_elections.html', {
                    "page": "Elections",
                    "error": response['error'], 
                    "user": user,
                    "elections": elections
                })
            
        else:
            end_setting = request.POST.get('end_setting')
            start_election = request.POST.get('start_election')
            end_election = request.POST.get('end_election')
            start_disclosure = request.POST.get('start_disclosure')
            description = request.POST.get('description')

            try:
                end_setting = datetime.fromisoformat(end_setting)
                start_election = datetime.fromisoformat(start_election)
                end_election = datetime.fromisoformat(end_election)
                start_disclosure = datetime.fromisoformat(start_disclosure)

            except ValueError:
                return render(request, 'admin/create_elections.html', {
                    "page": "Elections",
                    "error": ValueError, 
                    "user": user,
                    "elections": elections
                })
            
            response = create_election(end_setting, start_election, end_election, start_disclosure, description)
            elections = get_elections()["data"]

            if response['success']:
                return render(request, 'admin/create_elections.html', {
                    "page": "Elections",
                    "message": response['message'], 
                    "user": user,
                    "elections": elections
                })
            else:
                return render(request, 'admin/create_elections.html', {
                    "page": "Elections",
                    "error": response['error'], 
                    "user": user,
                    "elections": elections
                })

    except Exception as e:
        print(e)
        return redirect('login')


def create_voters(request):
    if 'access' not in request.session:
        redirect('login')

    if not is_staff(request.session['user']):
        redirect('login')

    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_elections()['data']
        voters = get_voters()['data']

        if request.method != 'POST':
            return render(request, 'admin/create_voters.html', {
                "page": "Voters",
                "user": user,
                "elections": elections,
                "voters": voters
            })
        
        if 'delete_cpf' in request.POST:
            delete_electionid, delete_cpf = request.POST.get('delete_cpf').split()
            response = delete_voter(delete_cpf, delete_electionid)

            voters = get_voters()['data']
            
            if response['success']:
                return render(request, 'admin/create_voters.html', {
                    "page": "Voters",
                    "message": response['message'], 
                    "user": user,
                    "elections": elections,
                    "voters": voters
                })
            
            else:
                return render(request, 'admin/create_voters.html', {
                    "page": "Voters",
                    "error": response['error'], 
                    "user": user,
                    "elections": elections,
                    "voters": voters
                })
            
        else:
            voter_name = request.POST.get('name')
            voter_cpf = request.POST.get('cpf')
            electionid = request.POST.get('electionid')
            response = create_voter(voter_name, voter_cpf, electionid)

            voters = get_voters()["data"]

            if response['success']:
                return render(request, 'admin/create_voters.html', {
                    "page": "Voters",
                    "message": response['message'], 
                    "user": user,
                    "elections": elections,
                    "voters": voters
                })
            
            else:
                return render(request, 'admin/create_voters.html', {
                    "page": "Voters",
                    "error": response['error'], 
                    "user": user,
                    "elections": elections,
                    "voters": voters
                })

    except:
        return redirect('login')
    

def create_offices(request):
    if 'access' not in request.session:
        redirect('login')

    if not is_staff(request.session['user']):
        redirect('login')

    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_elections()["data"]
        offices = get_offices()["data"]

        if request.method != 'POST':
            return render(request, 'admin/create_offices.html', {
                "page": "Offices",
                "user": user,
                "elections": elections,
                "offices": offices
            })
        
        if 'delete_office' in request.POST:
            delecte_election, delete_name = request.POST.get('delete_office').split()
            response = delete_office(delete_name, delecte_election)

            offices = get_offices()['data']

            if response['success']:
                return render(request, 'admin/create_offices.html', {
                    "page": "Offices",
                    "message": response['message'],
                    "user": user,
                    "elections": elections,
                    "offices": offices
                })

            else:
                return render(request, 'admin/create_offices.html', {
                    "page": "Offices",
                    "error": response['error'],
                    "user": user,
                    "elections": elections,
                    "offices": offices
                })
            
        else:
            office_name = request.POST.get('office_name')
            electionid = request.POST.get('electionid')
            response = create_office(office_name, electionid)

            offices = get_offices()['data']

            if response['success']:
                return render(request, 'admin/create_offices.html', {
                    "page": "Offices",
                    "message": response['message'],
                    "user": user,
                    "elections": elections,
                    "offices": offices
                })

            else:
                return render(request, 'admin/create_offices.html', {
                    "page": "Offices",
                    "error": response['error'],
                    "user": user,
                    "elections": elections,
                    "offices": offices
                })

    except:
        return redirect('login')


def candidate_page(request):
    if 'access' not in request.session:
        redirect('login')

    if not is_staff(request.session['user']):
        redirect('login')

    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_elections()['data']

        candidate_list = []
        for election in elections:
            candidates = get_candidates(election['electionid'])['data']
            for candidate in candidates:
                candidate_list.append(candidate)

        print(candidate_list)

        if request.method != 'POST':
            return render(request, 'admin/candidates.html', {
                "page": "Candidates",
                "user": user,
                "candidates": candidate_list
            })
        
        electionid, cpf_c, office_name = request.POST.get('approve_candidate').split()

        response = approve_candidate(cpf_c, electionid, office_name)

        if response['success']:
            approve_voter(cpf_c, electionid)

            candidate_list = []
            for election in elections:
                candidates = get_candidates(election['electionid'])['data']
                for candidate in candidates:
                    candidate_list.append(candidate)

            return render(request, 'admin/candidates.html', {
                "page": "Candidates",
                "message": response['message'],
                "user": user,
                "candidates": candidate_list
            })
        
        else:
            return render(request, 'admin/candidates.html', {
                "page": "Candidates",
                "error": response['error'],
                "user": user,
                "candidates": candidate_list
            })
            
    except:
        return redirect('login')


def voting_page(request):
    if 'access' not in request.session:
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        electionid = request.GET.get('electionid') or request.POST.get('electionid')
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        election = get_election(electionid)['data']
        voter = get_voter(cpf, electionid)['data']

        if request.method != 'POST':
            return render(request, 'home/voting_page.html', {
                'page': f"Election: {election['description']}",
                'user': user,
                'voter': voter,
                'election': election,
            })
        
        current_time = datetime.now()
        end_election = datetime.strptime(election['end_election'], "%a, %d %b %Y %H:%M:%S %Z")
        if current_time > end_election:
            return render(request, 'home/voting_page.html', {
                'page': f"Election: {election['description']}",
                'error': 'Election already finished.',
                'user': user,
                'voter': voter,
                'election': election,
            })
            

        ballot = {"election": electionid, "votes": {}}
        for office in election['offices']:
            office_name = office['office_name']
            candidate_name = request.POST.get(office_name)
            if candidate_name:
                ballot['votes'][office_name] = candidate_name

        clean_ballot = str(ballot)
        print(clean_ballot)

        ballot = pickle.dumps(ballot)

        result = prepare_ballot(ballot)
        enc_ballot = result['enc_ballot']
        ephemeral_key = result['ephemeral_key']
        pub_key_tallier = result['pub_key']

        if request.POST.get('audit'):
            return render(request, 'home/voting_page.html', {
                'message': 'vote successfully casted',
                'page': f"Election: {election['description']}",
                'user': user,
                'voter': voter,
                'election': election,
                'ballot': clean_ballot,
                'enc_ballot': enc_ballot,
                'ephemeral_key': ephemeral_key,
                'pub_key': pub_key_tallier
            })
        
        password = request.POST.get('password')
        
        salt = get_salt(user['password'])
        p_hash = create_hash(password, salt)

        response = verify_ballot(enc_ballot, p_hash, cpf, electionid)

        if not response['success']:
            return render(request, 'home/voting_page.html', {
                'error': response['error'],
                'page': f"Election: {election['description']}",
                'user': user,
                'voter': voter,
                'election': election,
            })
        
        credential = response['credential']
        signed_ballot = response['signed_ballot']
        
        cast_ballot(signed_ballot, enc_ballot, credential, electionid)

        return render(request, 'home/voting_page.html', {
                'message': 'vote successfully casted',
                'page': f"Election: {election['description']}",
                'user': user,
                'voter': voter,
                'election': election,
            })
    
    except (TokenError, InvalidToken):
        return redirect('login')


def commit_page(request):
    if 'access' not in request.session:
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']
        
        if is_staff(cpf):
            path = 'admin/commits.html'
            itens = get_elections()['data']

        else:
            path = 'home/commits.html'
            itens = get_voters_by_cpf(cpf)['data']

        commits = [{
            'electionid': item['electionid'],
            'description': item['description'],
            'commits': get_commits(item['electionid'])['data']
        } for item in itens]

        return render(request, path, {
            "page": "Commits",
            "user": user,
            "elections": commits
        })
    
    except (TokenError, InvalidToken):
        return redirect('login')
    

def authentication_page(request):
    if 'access' not in request.session:
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_voters_by_cpf(cpf)['data']

        current_time = datetime.now()

        if request.method != 'POST':
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "user": user,
                "elections": elections,
            })
        
        electionid = request.POST.get('electionid')
        password = request.POST.get('password')

        election = next((e for e in elections if str(e['electionid']) == str(electionid)), None)

        end_setting = datetime.strptime(election['end_setting'], "%a, %d %b %Y %H:%M:%S %Z")
        if current_time > end_setting:
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "error": 'authentication is not available anymore',
                "user": user,
                "elections": elections,
            })

        if not verify_hash(password, user['password']):
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "error": "Wrong password",
                "user": user,
                "elections": elections,
            })
        
        voter = get_voter(cpf, electionid)['data']

        if voter['auth'] == 1:
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "error": "Voter already authenticated",
                "user": user,
                "elections": elections,
            })
        
        response = authentication(user['name'], cpf, electionid, password)

        if response['success']:
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "success": response['message'],
                "user": user,
                "elections": elections,
            })
        
        else:
            return render(request, 'home/authenticate.html', {
                "page": "Authentication Page",
                "error": response['error'],
                "user": user,
                "elections": elections,
            })

    except (TokenError, InvalidToken):
        return redirect('login')

     
def applying_page(request):
    if 'access' not in request.session:
        redirect('login')

    try:
        access_token = AccessToken(request.session['access'])
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        elections = get_voters_by_cpf(cpf)['data']

        current_time = datetime.now()

        offices = []
        for election in elections:
            office_by_election = get_offices_by_election(election['electionid'])['data']
            for office in office_by_election:
                offices.append({
                    'electionid': election['electionid'],
                    'office_name': office[0]
                })

        if request.method != 'POST':
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "user": user,
                "elections": elections,
                "offices": offices,
            })
        
        electionid = request.POST.get('electionid')
        office_name = request.POST.get('office')
        password = request.POST.get('password')

        election = next((e for e in elections if str(e['electionid']) == str(electionid)), None)
        
        end_setting = datetime.strptime(election['end_setting'], "%a, %d %b %Y %H:%M:%S %Z")
        if current_time > end_setting:
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "error": "Applying is not available anymore",
                "user": user,
                "elections": elections,
                "offices": offices,
            })
        
        if not verify_hash(password, user['password']):
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "error": "Password does not match",
                "user": user,
                "elections": elections,
                "offices": offices,
            })
        
        voter = get_voter(cpf, electionid)['data']
        
        if voter['auth'] == 0:
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "error": "Voter is not authenticated",
                "user": user,
                "elections": elections,
                "offices": offices,
            })
        
        response = applying(cpf, electionid, office_name)

        if response['success']:
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "success": "Voter successfully applied, wait for admin confirmation",
                "user": user,
                "elections": elections,
                "offices": offices,
            })
        
        else:
            return render(request, 'home/apply.html', {
                "page": "Apply for an office",
                "error": response['message'],
                "user": user,
                "elections": elections,
                "offices": offices,
            })

    except (TokenError, InvalidToken):
        return redirect('login')


def election_page_admin(request):
    if 'access' not in request.session:
        return redirect('login')
    
    if not is_staff(request.session['user']):
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        electionid = request.GET.get('electionid') or request.POST.get('electionid')
        user = get_user(request.session['user'])['data']
        cpf = user['username']

        election = get_election(electionid)['data']

        if request.method != 'POST':
            return render(request, 'admin/election.html', {
                "page": f"Election: {election['description']}",
                "electionid": election['electionid'],
                "user": user,
                "election": election
            })
        
        end_setting = request.POST.get('end_setting')
        start_election = request.POST.get('start_election')
        end_election = request.POST.get('end_election')
        start_disclosure = request.POST.get('start_disclosure')
        description = request.POST.get('description')

        end_setting = datetime.fromisoformat(end_setting)
        start_election = datetime.fromisoformat(start_election)
        end_election = datetime.fromisoformat(end_election)
        start_disclosure = datetime.fromisoformat(start_disclosure)

        response = update_election(electionid, end_setting, start_election, end_election, start_disclosure, description)

        if response['success']:
            election = get_election(electionid)['data']
            return render(request, 'admin/election.html', {
                "page": f"Election: {election['description']}",
                "message": response['message'],
                "electionid": election['electionid'],
                "user": user,
                "election": election
            })
        
        else:
            return render(request, 'admin/election.html', {
                "page": f"Election: {election['description']}",
                "error": response['error'],
                "electionid": election['electionid'],
                "user": user,
                "election": election
            })
        
    except (TokenError, InvalidToken):
        return redirect('login')  


def election_page(request):
    if 'access' not in request.session:
        return redirect('login')
    
    try:
        access_token = AccessToken(request.session['access'])
        electionid = request.GET.get('electionid') or request.POST.get('electionid')
        user = get_user(request.session['user'])['data']
        name = user['name']
        cpf = user['username']

        election = get_election(electionid)['data']
        voter = get_voter(cpf, electionid)['data']

        print(election)

        current_time = datetime.now()

        if request.method != 'POST':
            return render(request, 'home/election.html', {
                'page': f"Election: {election['description']}",
                'user': user,
                'voter': voter,
                'election': election,
            })
        
        if 'auth_password' in request.POST:
            auth_password = request.POST.get('auth_password')

            end_setting = datetime.strptime(election['end_setting'], "%a, %d %b %Y %H:%M:%S %Z")
            if current_time > end_setting:
                return render(request, 'home/election.html', {
                    'error': 'authentication is not available anymore',
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })                   

            if not verify_hash(auth_password, user['password']):
                return render(request, 'home/election.html', {
                    'error': 'password does not match.',
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })
            
            response = authentication(name, cpf, electionid, auth_password)
            if response['success']:
                election = get_election(electionid)['data']
                voter = get_voter(cpf, electionid)['data']

                return render(request, 'home/election.html', {
                    'success': response['message'],
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })
            
            else:
                return render(request, 'home/election.html', {
                    'error': response['error'],
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })
            
        if 'apply_password' in request.POST:
            office_name = request.POST.get('office_name')
            apply_password = request.POST.get('apply_password')

            print(office_name)

            end_setting = datetime.strptime(election['end_setting'], "%a, %d %b %Y %H:%M:%S %Z")
            if current_time > end_setting:
                return render(request, 'home/election.html', {
                    'error': 'applying is not available anymore',
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })  

            if not verify_hash(apply_password, user['password']):
                return render(request, 'home/election.html', {
                    'error': 'password does not match.',
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })
            
            response = applying(cpf, electionid, office_name)
            print(response)
            if response['success']:
                election = get_election(electionid)['data']
                voter = get_voter(cpf, electionid)['data']

                return render(request, 'home/election.html', {
                    'success': response['message'],
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })
            
            else:
                return render(request, 'home/election.html', {
                    'error': response['error'],
                    'page': f"Election: {election['description']}",
                    'user': user,
                    'voter': voter,
                    'election': election,
                })

    except (TokenError, InvalidToken):
        return redirect('login')    


def logout(request):
    request.session.flush()  # Limpa a sessão
    return redirect('login')  # Redireciona para a página de login

        
