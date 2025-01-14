from django.db import models
from django.utils.timezone import now


# Create your models here.
from products.models import Products,SizeVariant
from django.db import models
from django.contrib.auth.models import User
from userprofile.models import useraddress  # Import Address model
from Coupons.models import coupons

class AlOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'pending'),
        ('completed', 'completed'),
        ('canceled', 'canceled'),
        ('delivered','delivered')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(useraddress, on_delete=models.CASCADE,null=False)
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    real_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    coupon = models.ForeignKey(coupons, on_delete=models.CASCADE, null=True, blank=True) 
    razorpay_order_id = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(max_length=500,null=True,blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    

class AlOrderItem(models.Model):

    order = models.ForeignKey(AlOrder, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)
    coupon = models.ForeignKey(coupons,on_delete=models.SET_NULL,null=True,blank=True )
    status = models.CharField(max_length=10,default='pending')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(max_length=500,null=True,blank=True)
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
 