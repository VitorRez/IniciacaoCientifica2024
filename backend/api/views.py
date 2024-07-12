from django.shortcuts import render
from django.contrib.auth.models import User
from .serializers import UserSerializer, VoterSerializer
from .models import Voter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class AuthenticateVoterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            user = request.user
            print(user.password)
            print(data)
            if user.check_password(data):
                voter = Voter.objects.get(voterid=user.username)
                voter.auth = 1
                voter.save(update_fields=['auth'])
                return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@method_decorator(csrf_exempt, name='dispatch')
class ApplyingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            # Process the data here
            return Response({'status': 'success', 'data': data}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'status': 'error', 'message': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

