# Generated by Django 4.2.6 on 2023-11-13 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("logic", "0009_userinfo_profile_pic"),
        ("fileoperations", "0006_accesslog_user_email_accesslog_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="accesslog",
            name="org",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="logic.organizations",
            ),
        ),
    ]