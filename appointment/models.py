from django.db import models
from Doctor_Module.models import DoctorProfileModel
from Acoounts.models import TeenagerAndParent
from .tasks import appointmeant_delete_task

choice = (("CONFIRM","CONFIRM"),("PENDING","PENDING"),("DECLINED","DECLINED"))

class Appointment(models.Model):
    doctor = models.ForeignKey(DoctorProfileModel,on_delete=models.CASCADE)
    user = models.ForeignKey(TeenagerAndParent,on_delete=models.CASCADE)
    from_time = models.DateTimeField(db_index=True)
    to_time = models.DateTimeField(db_index=True)
    payment_status = models.CharField(choices=choice, max_length=15,db_index=True,default="PENDING")
    created_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def save(self,*args,**kwargs):

        save_ob = super().save(*args,**kwargs)
        appointmeant_delete_task.apply_async(
            args=[ self.id], 
            countdown=1 * 60  
        )
        return save_ob


class Payment(models.Model):
    amount = models.DecimalField(decimal_places=3,max_digits=10)
    
    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE)
