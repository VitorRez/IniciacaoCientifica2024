from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import VOTER

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password"
        ]
        #extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        voters = VOTER.objects.all()
        if voters.filter(voterid=validated_data['username']).exists():
            user = User.objects.create_user(**validated_data)
            return user
        else:
            raise Exception("User is not elegible for any election.")
    
class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VOTER
        fields = {
            "user",
            "cpf",
            "electionid",
        }

        extra_kwargs = {"user": {"read_only": True}}
        