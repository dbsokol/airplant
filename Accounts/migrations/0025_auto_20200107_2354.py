# Generated by Django 2.2.7 on 2020-01-07 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0024_auto_20200107_1859'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='customer_id',
        ),
        migrations.RemoveField(
            model_name='paymentdetails',
            name='payment_token',
        ),
        migrations.AddField(
            model_name='customer',
            name='braintree_customer_global_id',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='braintree_customer_id',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='braintree_payment_method_global_id',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='braintree_payment_method_token',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
