from django.db import models
from cloudinary.models import CloudinaryField

# Create your models here.
class catagory(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    image = CloudinaryField('image') 
    offer = models.CharField(max_length=10,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name
    
    

    

    
