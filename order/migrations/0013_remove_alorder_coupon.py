# Generated by Django 5.1.3 on 2025-01-03 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_alorder_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alorder',
            name='coupon',
        ),
    ]
