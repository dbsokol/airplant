# Generated by Django 2.2.7 on 2019-12-18 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0018_auto_20191218_0215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='billing_day_of_month',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
