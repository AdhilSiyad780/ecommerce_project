from django.db import models
from django.contrib.auth.models import User
from order.models import AlOrder



# Create your models here.
class transactions(models.Model):
    STATUS_CHOICES = [
        ('Returned', 'Returned'),
        ('Canceled', 'Canceled'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    order = models.ForeignKey(AlOrder,on_delete=models.CASCADE)
    payment_type= models.CharField(max_length=255,blank=True,null=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'payment_id : {self.id} - {self.status}'
    

