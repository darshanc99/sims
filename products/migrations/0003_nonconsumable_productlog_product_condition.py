# Generated by Django 2.2.5 on 2020-08-31 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20200808_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonconsumable_productlog',
            name='product_condition',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
