# Generated by Django 2.2.7 on 2019-12-18 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0019_auto_20191218_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentdetails',
            name='card_name',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
