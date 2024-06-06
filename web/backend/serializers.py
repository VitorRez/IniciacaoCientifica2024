from rest_framework import serializers
from .models import Voter

class VoterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ('id', 'name', 'cpf', 'electionid', 'pub_key',
                  'priv_key', 'nonce', 'hash', 'salt')
        
class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = ('name', 'cpf', 'electionid')