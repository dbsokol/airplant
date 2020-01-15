# Generated by Django 2.2.7 on 2020-01-09 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0026_subscription_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('amount', models.IntegerField(blank=True, default=None, null=True)),
                ('has_been_used', models.BooleanField(default=False)),
            ],
        ),
    ]
