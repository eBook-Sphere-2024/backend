from django.db import models
from django.contrib.auth.models import User

class ReaderAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userReader')
    ebook = models.ForeignKey('eBook.eBook', on_delete=models.CASCADE, related_name='bookReaded')
    currentPgae = models.IntegerField(default=1)
    highest_progress = models.IntegerField(default=1)
    totalPages = models.IntegerField(default=0)

    class Meta:
            unique_together = ('user', 'ebook')  # Ensure a user can only favorite a book once
    def __str__(self):
        return f"{self.user.username} - {self.ebook.title} - Highest Progress: {self.highest_progress}"