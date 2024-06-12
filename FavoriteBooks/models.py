# models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class FavoriteBooks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_books')
    ebook = models.ForeignKey('eBook.eBook', on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'ebook')  # Ensure a user can only favorite a book once

    def __str__(self):
        return f'{self.user.username} favorites {self.ebook.title}'
