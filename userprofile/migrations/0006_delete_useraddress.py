# Generated by Django 5.1.3 on 2024-12-02 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0005_remove_useraddress_address'),
    ]

    operations = [
        migrations.DeleteModel(
            name='useraddress',
        ),
    ]
