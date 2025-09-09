from django.db import models
from Acoounts.models import Accounts,TeenagerAndParent
from django.dispatch import receiver
from django.db.models.signals import post_delete
import logging
logger = logging.Logger(__name__)
import random
import string


class DoctorProfileModel(models.Model):
    accounts = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    doctor_type = models.CharField(max_length=256, null=True, blank=True) 
    amount = models.CharField(max_length=256, null=True, blank=True)
    experience = models.CharField(max_length=256, null=True, blank=True)
    about = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    average_rating = models.FloatField(blank=True,null=True,default=0.0)
    profile_pic = models.ImageField(blank=True,null=True,max_length=512) 

    def __str__(self):
        return f"{self.accounts.email} - {self.doctor_type} "


@receiver(post_delete, sender=DoctorProfileModel)
def delete_doctor_when_accounts_delete(sender, instance, **kwargs):
    try:
        if instance.accounts:
            instance.accounts.delete()
    except:
        logger.error("error in deleting doctor while deleting account", exc_info=True)


class AvailableTime(models.Model):
    from_time = models.DateTimeField(db_index=True)
    to_time = models.DateTimeField(db_index=True)
    doctor = models.ForeignKey(DoctorProfileModel,on_delete=models.CASCADE,related_name="availability")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return (
            f"doctor : {self.doctor.accounts.username}\n"
            f" - from_time :{self.from_time}\n"
            f" - to_time :{self.to_time}"
        )

    class Meta:
        ordering = ['from_time']
    
class ReviewAndRating(models.Model):
    user = models.ForeignKey(TeenagerAndParent,on_delete=models.SET_NULL,null=True,blank=True)
    doctor = models.ForeignKey(DoctorProfileModel,on_delete=models.CASCADE,related_name="reviews")
    review = models.TextField()
    rating = models.FloatField()

    def __str__(self):
        return f'{self.doctor.accounts.username} - {self.user.account.username}'
    

class DoctorProfileModelEdit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    accounts = models.ForeignKey(DoctorProfileModel, on_delete=models.CASCADE, related_name="doctor_profile_edits")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    request_id = models.TextField(null=True, blank=True)

    def save(self,*args,**kwargs):
        characters = string.ascii_letters + string.digits  
        while True :
            unique = ''.join(random.choice(characters) for _ in range(12))
            unique = "#" + unique
            if not DoctorProfileModelEdit.objects.filter(request_id=unique).exists():
                self.request_id = unique
                break
        
        return super().save(*args,**kwargs)

    def __str__(self):
        return f"Edit Session for {self.accounts.accounts.username} - Status: {self.status}"
 

class DoctorProfileFieldEdit(models.Model):
    doctor_profile_edit = models.ForeignKey(DoctorProfileModelEdit, on_delete=models.CASCADE, related_name="field_edits")
    field_name = models.CharField(max_length=50)  
    field_value = models.TextField()  

    def __str__(self):
        return f"Field Edit: {self.field_name} - Value: {self.field_value}"




