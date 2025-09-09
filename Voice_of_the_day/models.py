from django.db import models
from Acoounts.models import Accounts, Concentrate, TeenagerAndParent
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
import logging

logger = logging.getLogger(__name__)

class VoiceOfTheDay(models.Model):
    title = models.CharField(max_length=256, blank=True, null=True)
    content = models.CharField(max_length=256, blank=True, null=True)
    image = models.ImageField(upload_to="VoiceOfTheDay_Image/", blank=True, null=True)
    concentrates = models.ManyToManyField(Concentrate, blank=True)
    person_likes = models.ManyToManyField(TeenagerAndParent, blank=True)
    total_likes = models.IntegerField(default=0)
    publish_by = models.ForeignKey(Accounts, on_delete=models.DO_NOTHING, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'

@receiver(post_delete, sender=VoiceOfTheDay)
def delete_voice_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
            logger.debug(f"Image removed {instance.image.path}")
            
        else:
            logger.debug(f"Image not found: {instance.image.path}")