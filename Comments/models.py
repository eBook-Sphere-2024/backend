from django.db import models

class Comment(models.Model):
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='user')
    book = models.ForeignKey('eBook.eBook', on_delete=models.CASCADE, related_name='book')
    content = models.TextField()
    publish_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content
    