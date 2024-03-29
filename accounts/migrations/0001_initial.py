# Generated by Django 5.0.1 on 2024-02-13 23:01

import accounts.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('short_code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=10)),
                ('country', models.CharField(max_length=50)),
                ('phone_number', models.CharField(blank=True, max_length=15, unique=True)),
                ('contact_person', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WaitingList',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('is_registered', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('short_code', models.CharField(max_length=10, unique=True)),
                ('long_name', models.CharField(max_length=100)),
                ('short_name', models.CharField(blank=True, max_length=9)),
                ('description', models.TextField(blank=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.institution')),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_enrolled', models.DateField(auto_now_add=True)),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email_notifications', models.BooleanField(default=True)),
                ('sms_notifications', models.BooleanField(default=False)),
                ('language', models.CharField(default='en', max_length=2)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('account_type', models.CharField(choices=[(accounts.models.ProfileType['STUDENT'], 'student'), (accounts.models.ProfileType['INSTRUCTOR'], 'instructor'), (accounts.models.ProfileType['ADMIN'], 'admin')], max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=15, unique=True)),
                ('is_2fa_enabled', models.BooleanField(default=False)),
                ('streak_days', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
