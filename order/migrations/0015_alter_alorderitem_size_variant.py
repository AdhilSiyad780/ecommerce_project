# Generated by Django 5.1.3 on 2025-01-04 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_alorder_coupon'),
        ('products', '0005_review_ration_delete_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alorderitem',
            name='size_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.sizevariant'),
        ),
    ]
