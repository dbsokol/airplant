# Generated by Django 2.2.7 on 2019-12-18 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0003_auto_20191218_0215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription_archive',
            name='billing_day_of_month',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
