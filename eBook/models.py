from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class eBook(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    publication_date = models.DateField()
    content = models.CharField(max_length=2000, validators=[URLValidator()])
    cover = models.CharField(max_length=2000, validators=[URLValidator()])
    categories = models.ManyToManyField(Category, related_name='bookCategory' )

    def __str__(self):
        return self.title

