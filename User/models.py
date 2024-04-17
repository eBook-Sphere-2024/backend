from django.db import models
from django.core.validators import URLValidator

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    registered_date = models.DateField(auto_now_add=True)
    profile_image = models.CharField(max_length=2000)

    def __str__(self):
        return self.username
