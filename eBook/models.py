from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from User.models import User
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class eBook(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name='author')
    description = models.TextField()
    publication_date = models.DateField(auto_now_add=True)
    content = models.CharField(max_length=2000)
    cover = models.CharField(max_length=2000)
    categories = models.ManyToManyField(Category, related_name='bookCategory' )

    def __str__(self):
        return self.title

