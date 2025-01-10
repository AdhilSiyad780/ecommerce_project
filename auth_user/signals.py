from django.db.models import post_save
from django.dispatch import receiver
from auth_user.models import Refferal
from django.contrib.auth.models import User

f

@receiver(post_save,sender=User)
def create_user_refferal(sender,instance,created,**kwags):
    if created:
        Refferal.objects.create(user=instance)


def save_user_profile(sender,instance,**kwags):
    instance.refferal.save()