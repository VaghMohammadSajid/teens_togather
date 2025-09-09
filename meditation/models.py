from django.db import models
from Acoounts.models import Accounts

# Create your models here.


class MeditationCategory(models.Model):
    name = models.CharField(max_length=256,unique=True)
    image = models.ImageField(upload_to="category_image",blank=True,null=True)
    about = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name


class MeditationAudio(models.Model):
    title = models.CharField(max_length=256)
    audio = models.FileField(upload_to='audio_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Accounts,on_delete=models.CASCADE)
    category = models.ForeignKey(MeditationCategory, on_delete=models.SET_NULL, null=True, blank=True,related_name="cate")

    def __str__(self):
        return self.title

