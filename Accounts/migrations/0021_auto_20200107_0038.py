# Generated by Django 2.2.7 on 2020-01-07 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0020_paymentdetails_card_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentdetails',
            old_name='card_name',
            new_name='card_holder_name',
        ),
    ]
