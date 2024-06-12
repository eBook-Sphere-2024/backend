from django.db import models
from django.contrib.auth.models import User
from Template.models import Template
from django.core.validators import MinValueValidator, MaxValueValidator

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
    

    def __str__(self):
        return self.title

class Rating(models.Model):
    ebook = models.ForeignKey('eBook', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        unique_together = ('ebook', 'user')  # Ensure a user can rate an ebook only once

    def __str__(self):
        return f'{self.user} rated {self.ebook} as {self.rate}'