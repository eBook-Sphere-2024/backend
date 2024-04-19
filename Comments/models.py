from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    ebook = models.ForeignKey('eBook.eBook', on_delete=models.CASCADE, related_name='book')
    content = models.TextField()
    publish_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content