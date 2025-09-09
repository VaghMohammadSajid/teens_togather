from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
import uuid
import random
import string
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
# from .apps import BLOCKLIST
# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,phone_number,designation,email,password=None):
        if not email:
            raise ValueError('user must have an email')
        if  password is None:
            raise ValueError('must need password')

        if not username:
            raise ValueError('must need username')
        user = self.model(email=self.normalize_email(email), username=username, first_name=first_name,
                          last_name=last_name, phone_number=phone_number, designation=designation)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self,first_name,last_name,phone_number,designation,username,email,password = None):

        user = self.create_user(email=self.normalize_email(email), first_name=first_name, last_name=last_name,
                                username=username, phone_number=phone_number, designation=designation,password=password)
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user








choice = (("DOC","DOC"),("TEENS","TEENS"),("PARENTS","PARENTS"),("ADMIN","ADMIN"))


class Accounts(AbstractBaseUser):
    first_name = models.CharField(max_length=256,blank=True,null=True,db_index=True)
    last_name = models.CharField(max_length=256,blank=True,null=True,db_index=True)

    username = models.CharField(max_length=256,unique=True,db_index=True)
    email = models.EmailField(max_length=256,unique=True,db_index=True)
    phone_number = models.CharField(max_length=15,unique=True,db_index=True)


    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_delete  = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    referal_code = models.UUIDField(default=uuid.uuid4,null=True,blank=True)
    designation = models.CharField(choices=choice, max_length=8,db_index=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username','first_name','last_name','phone_number','designation']

    objects = AccountManager()
    def __str__(self):
        return self.username

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,add_label):
        return True

class Concentrate(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return f'{self.name}'
    
class Avatar(models.Model):
    image = models.FileField(upload_to='avatar')

class TeenagerAndParent(models.Model):
    account = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    concentrate_on = models.ManyToManyField(Concentrate)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    avatar = models.ForeignKey(Avatar,on_delete=models.PROTECT,null=True,blank=True)
    nick_name = models.CharField(max_length=254,null=True,blank=True,db_index=True)

    def __str__(self):
        return f'{self.account}'


class StoreOtpForEmail(models.Model):
    unique_key = models.CharField(max_length=12,blank=True,null=True)
    email = models.CharField(max_length=256,blank=True,null=True)
    otp = models.CharField(max_length=5)

    def __str__(self,*args,**kwargs):
        return f'{self.email} - {self.otp}'
    def save(self,*args,**kwargs):
        while True:
            random = generate_random()
            if not StoreOtpForEmail.objects.filter(unique_key=random).exists():
                break
        self.unique_key = random
        super().save(*args,**kwargs)
class StoreOtpForPhone(models.Model):
    unique_key = models.CharField(max_length=12,blank=True,null=True)
    number = models.CharField(max_length=24,blank=True,null=True)
    otp = models.CharField(max_length=5)

    def __str__(self):
        return f'{self.number} - {self.otp}'
    def save(self,*args,**kwargs):
        while True:
            random = generate_random()
            if not StoreOtpForPhone.objects.filter(unique_key=random).exists():
                break
        self.unique_key = random
        return  super().save(*args, **kwargs)
        



def generate_random():
    characters = string.ascii_letters + string.digits  # Includes both alphabets and digits
    return ''.join(random.choice(characters) for _ in range(12))



choice = (("CHATROOM", "CHATROOM"), ("HAPPYMOMENTS", "HAPPYMOMENTS"), 
          ("DOCLIST", "DOCLIST"), ("MEDITATION-CATE-LIST", "MEDITATION-CATE-LIST"), 
          ("MEDITATION-AUDIO-LIST", "MEDITATION-AUDIO-LIST"))
class FeatureToggles(models.Model):
    disable_feature = models.CharField(choices=choice, max_length=256,unique=True)
    disable_reason = models.TextField(null=True, blank=True)



@receiver(post_save, sender=FeatureToggles)
def feature_toggle_post_save(sender, instance, created, **kwargs):
    from Acoounts.apps import  BLOCKLIST

    if created:
        BLOCKLIST.append(instance.disable_feature)

@receiver(post_delete, sender=FeatureToggles)
def feature_toggle_post_delete(sender, instance, **kwargs):
    from Acoounts.apps import  BLOCKLIST
    BLOCKLIST.remove(instance.disable_feature) 
   



class Notification(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"