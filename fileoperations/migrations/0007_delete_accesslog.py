# Generated by Django 4.2.6 on 2023-10-28 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fileoperations', '0006_accesslog'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AccessLog',
        ),
    ]