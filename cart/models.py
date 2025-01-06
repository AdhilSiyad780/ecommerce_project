from django.db import models
from django.contrib.auth.models import User
from products.models import Products

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'Cart of {self.user.username}'
    
class Cartitems(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    size = models.CharField(max_length=10,default='M')
    def total_priced(self):
        return self.product.price*self.quantity
    def __str__(self):
        return super().__str__()
    def return_stock(self):
        return  f"self.product.size_variant.stock"
        
