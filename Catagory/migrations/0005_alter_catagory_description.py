# Generated by Django 5.1.3 on 2024-12-01 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Catagory', '0004_alter_catagory_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catagory',
            name='description',
            field=models.CharField(max_length=100),
        ),
    ]
