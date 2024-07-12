from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

# Create your models here.

class Election(models.Model):
    electionid = models.IntegerField(primary_key=True)
    year = models.DateField(default=datetime.now().year, null=False)
    num_offices = models.IntegerField()

    def __int__(self):
        return self.Election.electionid

class Voter(models.Model):
    class Meta:
        unique_together = (('voterid', 'electionid'),)

    name = models.TextField(default=" ")
    voterid = models.IntegerField(primary_key=True, null=False)
    electionid = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="election")
    auth = models.SmallIntegerField(default=0)
    pub_key = models.BinaryField()
    priv_key = models.BinaryField()
    nonce = models.BinaryField()
    hash = models.BinaryField()
    salt = models.BinaryField()

    def __int__(self):
        return self.voterid



    