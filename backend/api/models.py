from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

# Create your models here.

class Election(models.Model):
    electionid = models.IntegerField(primary_key=True)
    year = models.IntegerField(default=datetime.now().year, null=False)
    num_offices = models.IntegerField()

    def __str__(self):
        return f"Election {self.electionid} - {self.year}"

class Voter(models.Model):
    name = models.TextField(default=" ")
    voterid = models.IntegerField()
    electionid = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="election")
    auth = models.SmallIntegerField(default=0)
    pub_key = models.TextField()
    priv_key = models.BinaryField()
    nonce = models.BinaryField()
    hash = models.BinaryField()
    salt = models.BinaryField()

    class Meta:
        unique_together = (('voterid', 'electionid'),)
    
    def __str__(self):
        return f"{self.voterid} - {self.electionid}"
    
class Offices(models.Model):
    class Meta:
        unique_together = (('name', 'electionid'))

    name = models.TextField(default=" ")
    electionid = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="electionid_office")
    digit_num = models.IntegerField()

    def __str__(self):
        return self.name


    