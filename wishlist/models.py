from django.db import models
from products.models import Products
from django.contrib.auth.models import User


# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Cart of {self.user.username}'
    
class Wishlistitems(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE,related_name='wish')
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    quantity = models.PositiveBigIntegerField(default=1)
    def total_priced(self):
        return self.product.price*self.quantity
     