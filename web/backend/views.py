from django.shortcuts import render
from rest_framework import generics, status
from .models import Voter
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import VoterSerializer, AccessPageSerializer

# Create your views here.

class VoterView(generics.CreateAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer

class AccessPageView(APIView):
    serializer_class = AccessPageSerializer

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.data.get('name')
            cpf = serializer.data.get('cpf')
            electionid = serializer.data.get('electionid')
            print(name, cpf, electionid)
            queryset = Voter.objects.filter(cpf=cpf, electionid=electionid)
            if queryset.exists():
                voter = queryset[0]
                voter.name = name
                voter.cpf = cpf
                voter.electionid = electionid
                voter.save(update_fields=['name', 'cpf', 'electionid'])
                return Response(VoterSerializer(voter).data, status=status.HTTP_200_OK)
            else:
                voter = Voter(name=name, cpf=cpf, electionid=electionid)
                voter.save()
                return Response(VoterSerializer(voter).data, status=status.HTTP_201_CREATED)
        
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
