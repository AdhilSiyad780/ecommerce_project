# Generated by Django 5.1.3 on 2024-12-04 14:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0009_alter_useraddress_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraddress',
            name='country',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='district',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='house_name',
        ),
    ]
