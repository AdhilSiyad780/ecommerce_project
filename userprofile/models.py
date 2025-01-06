from django.db import models
from django.contrib.auth.models import User


#Create your models here.
class useraddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    fullname = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=10)
    landmark = models.CharField(50)
    phone_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateField(auto_now_add=True)
    def __str__(self):
        return super().__str__()
