# Generated by Django 4.2.6 on 2023-10-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0008_users_is_approved_users_is_authenticated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='role',
            field=models.CharField(blank=True, default='employee', max_length=255, null=True),
        ),
    ]
