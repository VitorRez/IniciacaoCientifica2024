from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Voter(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voter", null=True)
    election = models.IntegerField()
    auth = models.SmallIntegerField()
    candidate = models.SmallIntegerField()
    #pub_key = models.BinaryField()
    #priv_key = models.BinaryField()
    #nonce = models.BinaryField()
    #hash = models.BinaryField()
    #salt = models.BinaryField()

    def __int__(self):
        return self.election

    