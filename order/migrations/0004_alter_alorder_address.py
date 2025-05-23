# Generated by Django 5.1.3 on 2024-12-14 08:47

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_alorder_address'),
        ('userprofile', '0010_remove_useraddress_country_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alorder',
            name='address',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.CASCADE, to='userprofile.useraddress'),
            preserve_default=False,
        ),
    ]
