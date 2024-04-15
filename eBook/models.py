from django.db import models
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

    def __str__(self):
        return self.title
    
class eBookCategory(models.Model):
    ebook = models.ForeignKey(eBook, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.ebook.title} - {self.category.name}"
