from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


# Create your models here.

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def is_expired(self):
        return timezone.now() > self.expires_at
    
class Refferal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    refferal_code = models.CharField(max_length=10,unique=True,blank=True)
    reffered_by = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name='referrals')
    def save(self,*args,**kwargs):
        if not self.refferal_code :
            self.refferal_code=get_random_string(10).upper()
        super().save(*args,**kwargs)
    