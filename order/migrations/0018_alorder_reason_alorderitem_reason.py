# Generated by Django 5.1.3 on 2025-01-13 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_alorder_real_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='alorder',
            name='reason',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='alorderitem',
            name='reason',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
