# Generated by Django 2.2.6 on 2020-03-01 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20200301_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccounts',
            name='email',
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
    ]