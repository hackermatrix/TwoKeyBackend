# Generated by Django 4.2.6 on 2024-01-31 11:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fileoperations", "0030_alter_accesslog_profile_pic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accesslog",
            name="file_name",
            field=models.CharField(default="", max_length=500),
        ),
        migrations.AlterField(
            model_name="accesslog",
            name="username",
            field=models.CharField(default="", max_length=100),
        ),
    ]
