from django.db import models
from Catagory.models import catagory
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User

# Create your models here.

class Products(models.Model):
    catagory = models.ForeignKey(catagory,on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    offer = models.DecimalField(max_digits=8,decimal_places=2)
    image1 = CloudinaryField('image')
    image2 = CloudinaryField('image')
    image3 = CloudinaryField('image')
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0,null=True,blank=True)

 
    def __str__(self):
        return self.name
    
class SizeVariant(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='size_variant')
    size = models.CharField(max_length=15)
    stock = models.PositiveIntegerField(default=0)
    def __str__(self):
        return super().__str__()
    
class Review_ration(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='rate_review')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating as 1 to 5 scale
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Review for {self.product.name} by {self.rating} stars'


