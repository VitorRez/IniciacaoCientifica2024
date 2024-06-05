from django.db import models

# Create your models here.

class Voter(models.Model):
    name = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11, unique=True)
    electionid = models.CharField(max_length=3)
    password = models.CharField(max_length=20)