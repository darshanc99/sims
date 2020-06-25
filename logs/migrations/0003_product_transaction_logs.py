# Generated by Django 2.2.5 on 2020-06-25 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0002_auto_20200619_0138'),
    ]

    operations = [
        migrations.CreateModel(
            name='product_transaction_logs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=40)),
                ('timestamp', models.DateTimeField(blank=True, default=None)),
                ('message', models.CharField(blank=True, max_length=500)),
            ],
        ),
    ]