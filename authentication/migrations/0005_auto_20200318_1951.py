# Generated by Django 2.2.6 on 2020-03-18 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_useraccounts_accountstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccounts',
            name='accountstatus',
            field=models.BooleanField(default=True),
        ),
    ]
