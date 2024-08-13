from django.shortcuts import render
from django.contrib.auth.models import User
from .serializers import UserSerializer, VoterSerializer
from .models import Voter, Offices, Election
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views import View
from django.http import JsonResponse
from .clients.crypto.ciphers import *
from .clients.crypto.PBKDF import *
from .clients.election_client import *
from .clients.reg_client import *
from .clients.adm_client import *

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class AuthenticateVoterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            user = request.user

            password = data.get('password')
            electionid = data.get('election')

            print(user.password)
            
            if user.check_password(password):
                voter = Voter.objects.get(voterid=user.username, electionid=electionid)
                msg = '1 ' + voter.name + ' ' + str(voter.voterid) + ' ' + str(electionid) + ' ' + password
                print(msg)
                salt, nonce, enc_key, hash, cert = authentication(msg)
                voter.auth = 1
                voter.pub_key = cert
                voter.priv_key = enc_key
                voter.nonce = nonce
                voter.hash = hash
                voter.salt = salt
                voter.save()
                return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
            else:
                print(1)
                return Response({'status': 'error', 'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            print(2)
            return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@method_decorator(csrf_exempt, name='dispatch')
class ApplyingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data

            # Ensure data is in dictionary format
            password = data.get('password')
            electionid = data.get('election')
            officeid = data.get('officeid')
            campaignid = data.get('campaignid')

            print(user.password)
            print(password)
            print(type(password))

            voter = Voter.objects.get(voterid=user.username, electionid=electionid)

            x = verify_hash(password, voter.hash)

            if x:
                info = str(voter.voterid) + " " + str(electionid) + " " + str(officeid) + " " + str(campaignid)
                pub_key = search_public_key(voter.pub_key)
                priv_key = search_private_key(password, voter.salt, voter.nonce, voter.hash, voter.priv_key)
                print(info)
                print(pub_key.export_key())
                print(priv_key)
                print(campaignid)
                send_to_adm(info, priv_key, pub_key.export_key())
                return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
            else:
                print(1)
                return Response({'status': 'error', 'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            print(2)
            return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class OfficesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            election_id = request.query_params.get('electionid')
            if not election_id:
                return Response({'status': 'error', 'message': 'Election ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            offices = Offices.objects.filter(electionid=election_id)
            offices_data = [{"id": office.id, "name": office.name} for office in offices]
            return Response({'status': 'success', 'data': offices_data}, status=status.HTTP_200_OK)
        except Election.DoesNotExist:
            return Response({'status': 'error', 'message': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class ElectionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all voters related to the logged-in user
            voters = Voter.objects.filter(voterid=request.user.username)
            
            # Collect all related election ids
            election_ids = voters.values_list('electionid', flat=True).distinct()
            
            # Fetch elections based on the collected election ids
            elections = Election.objects.filter(electionid__in=election_ids)
            elections_data = [{"electionid": election.electionid, "year": election.year} for election in elections]
            
            return Response({'status': 'success', 'data': elections_data}, status=status.HTTP_200_OK)
        except Voter.DoesNotExist:
            return Response({'status': 'error', 'message': 'Voter not found'}, status=status.HTTP_404_NOT_FOUND)
        except Election.DoesNotExist:
            return Response({'status': 'error', 'message': 'Election not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

