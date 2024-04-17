from django.db import models

class Template(models.Model):
    name = models.CharField(max_length=100)
    content = models.CharField(max_length=2000)
    cover = models.CharField(max_length=2000)
