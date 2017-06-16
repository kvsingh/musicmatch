from django.db import models

# Create your models here.
class Likes(models.Model):
    music_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)

