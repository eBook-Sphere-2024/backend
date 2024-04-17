from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from User.models import User
from Template.models import Template
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
    template = models.ForeignKey(Template, on_delete=models.CASCADE,related_name='template')

    def __str__(self):
        return self.title
    

    def __str__(self):
        return self.title

