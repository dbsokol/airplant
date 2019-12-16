# Generated by Django 2.2.7 on 2019-12-16 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0012_subscription_reason_for_canceling'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='subscription',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='Accounts.Subscription'),
        ),
    ]