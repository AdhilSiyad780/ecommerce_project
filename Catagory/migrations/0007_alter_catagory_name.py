# Generated by Django 5.1.3 on 2025-01-10 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Catagory', '0006_alter_catagory_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catagory',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
