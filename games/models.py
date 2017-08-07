from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Game(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField('date created')
    modified = models.DateTimeField('date modified')
    data = models.TextField()
    history = models.TextField()
    user = models.ForeignKey(User)
    

    
