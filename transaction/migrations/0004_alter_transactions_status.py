# Generated by Django 5.1.3 on 2025-01-05 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='status',
            field=models.CharField(max_length=30),
        ),
    ]
