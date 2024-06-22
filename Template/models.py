from django.db import models

class Template(models.Model):
    name = models.CharField(max_length=100)
    content = models.CharField(max_length=2000)
    cover = models.CharField(max_length=2000)
    previewurl = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.name
