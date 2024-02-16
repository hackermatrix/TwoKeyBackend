# Generated by Django 4.2.6 on 2024-02-16 09:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'departments',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Organizations',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, null=True, unique=True)),
            ],
            options={
                'db_table': 'organizations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('role', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'user_roles',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('username', models.CharField(default='', null=True)),
                ('name', models.CharField(default='')),
                ('last_name', models.CharField(default='')),
                ('email', models.EmailField(default=None, max_length=254)),
                ('phone', models.BigIntegerField(default=None, null=True)),
                ('profile_pic', models.URLField(default=None, null=True)),
                ('role_priv', models.CharField(default='employee', max_length=20)),
                ('country', models.CharField(default='', max_length=30)),
                ('state', models.CharField(default='', max_length=30)),
                ('city', models.CharField(default='', max_length=30)),
                ('postal_code', models.IntegerField(default=None, null=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_authenticated', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('dept', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='logic.departments')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logic.userinfo')),
                ('org', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='logic.organizations')),
            ],
            options={
                'db_table': 'user_info',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='departments',
            name='org',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='logic.organizations'),
        ),
    ]
