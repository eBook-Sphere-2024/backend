from django.db import models
from django.contrib.auth.models import User as DjangoUser

class UserProfile(models.Model):
    user= models.ForeignKey(DjangoUser, on_delete=models.CASCADE , related_name='user_profile')
    profile_image = models.CharField(max_length=2000 , default='https://drive.google.com/thumbnail?id=1cCbs7SU4Ph8j3bnweJsouYqnkOkhlsiH')

    def __str__(self):
        return self.user.username