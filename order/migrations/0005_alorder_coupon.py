# Generated by Django 5.1.3 on 2024-12-23 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coupons', '0003_alter_coupons_discount_value'),
        ('order', '0004_alter_alorder_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='alorder',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Coupons.coupons'),
        ),
    ]
