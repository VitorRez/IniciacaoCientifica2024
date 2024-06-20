from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, VoterSerializer
from .models import Voter
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CreateVoterList(generics.ListCreateAPIView):
    serializer_class = VoterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Voter.objects.filter(voter=user)
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(voter=self.request.user)
        else:
            print(serializer.errors)
