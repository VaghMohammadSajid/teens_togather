from django.db import models
from django.db import models
from Acoounts.models import Accounts, Concentrate, TeenagerAndParent
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
import logging
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

def validate_file_type(value):
    ext = os.path.splitext(value.name)[1]  # Get file extension
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov']
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed types are: jpg, jpeg, png, gif, mp4, avi, mov.'))

class HappyMoments(models.Model):
    title = models.CharField(max_length=256, blank=True, null=True)
    file = models.FileField(upload_to="happy_moments/", validators=[validate_file_type], blank=True, null=True)
    
    person_likes = models.ManyToManyField(TeenagerAndParent, blank=True)
    total_likes = models.IntegerField(default=0)
    publish_by = models.ForeignKey(TeenagerAndParent, on_delete=models.DO_NOTHING, blank=True, null=True,related_name="publish")
    create_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)  
    block = models.BooleanField(default=False)  


    def __str__(self):
        return f'{self.title}'

@receiver(post_delete, sender=HappyMoments)
def delete_voice_image(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
            logger.debug(f"Image removed {instance.file.path}")
            
        else:
            logger.debug(f"Image not found: {instance.file.path}")


class HappyMomentReport(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name='reports')
    happy_moment = models.ForeignKey(HappyMoments, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on Happy Moment {self.happy_moment.id}"


