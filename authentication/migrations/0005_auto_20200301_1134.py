# Generated by Django 2.2.6 on 2020-03-01 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20200301_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccounts',
            name='userrole',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]
