from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from pytz import timezone 

# Create your models here.

class ELECTION(models.Model):
    ELECTIONID = models.IntegerField(primary_key=True)
    YEAR = models.IntegerField(default=datetime.now().year, null=False)
    NUM_OFFICES = models.IntegerField()
    END_SETTING = models.DateTimeField(default=datetime.now(timezone('America/Sao_Paulo')))
    END_ELECTION = models.DateTimeField(default=datetime.now(timezone('America/Sao_Paulo')))

    def __str__(self):
        return str(self.ELECTIONID)

class VOTER(models.Model):
    NAME = models.TextField(default=" ")
    CPF = models.TextField()
    ELECTIONID = models.ForeignKey(ELECTION, on_delete=models.CASCADE)
    AUTH = models.IntegerField(default=0)
    CANDIDATE = models.IntegerField(default=0)
    PUB_KEY = models.TextField(default=" ")
    PRIV_KEY = models.BinaryField()
    SALT = models.BinaryField()

    class Meta:
        unique_together = (('CPF', 'ELECTIONID'),)
    
    def __str__(self):
        return f"{self.CPF} - {self.ELECTIONID}"
    
class OFFICE(models.Model):
    NAME = models.TextField(default=" ")
    ELECTIONID = models.ForeignKey(ELECTION, on_delete=models.CASCADE)
    DIGIT_NUM = models.IntegerField()

    class Meta:
        unique_together = (('NAME', 'ELECTIONID'))

    def __str__(self):
        return self.NAME