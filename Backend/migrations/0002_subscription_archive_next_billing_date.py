# Generated by Django 2.2.7 on 2019-12-18 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription_archive',
            name='next_billing_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
