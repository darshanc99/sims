# Generated by Django 2.2.5 on 2020-03-04 11:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_productlist_arrival_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='productlist',
            name='arrival_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 3, 4, 17, 8, 53, 127597)),
        ),
    ]
