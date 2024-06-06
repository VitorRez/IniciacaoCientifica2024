from django.db import models

# Create your models here.

class Voter(models.Model):
    name = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11)
    electionid = models.CharField(max_length=3)
    pub_key = models.BinaryField()
    priv_key = models.BinaryField()
    nonce = models.BinaryField()
    hash = models.BinaryField()
    salt = models.BinaryField()
