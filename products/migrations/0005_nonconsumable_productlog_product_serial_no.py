# Generated by Django 2.2.5 on 2020-07-09 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_nonconsumable_productlog_return_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='nonconsumable_productlog',
            name='product_serial_no',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
