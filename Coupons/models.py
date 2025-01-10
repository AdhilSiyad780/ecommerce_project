from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class coupons(models.Model):
    
    code = models.CharField(max_length=30,unique=True)
    discount_value =models.IntegerField()
    min_purchase_amount = models.DecimalField(max_digits=10,decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateField(auto_now=True)
    def __str__(self):
        return super().__str__()
    
class wallet(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return super().__str__()