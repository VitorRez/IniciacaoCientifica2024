from django.shortcuts import render
from rest_framework import generics, status
from .models import Voter
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import VoterSerializer

# Create your views here.

class VoterView(generics.CreateAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer

        

