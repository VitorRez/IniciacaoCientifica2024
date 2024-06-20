from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Voter

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "password"
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
    
class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = [
            "id",
            "voter",
            "election",
            "auth",
            "candidate",
            #"pub_key",
            #"priv_key",
            #"nonce",
            #"hash",
            #"salt"
        ]
        extra_kwargs = {"voter": {"read_only": True}}
    


