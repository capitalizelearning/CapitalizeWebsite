# Generated by Django 5.0.3 on 2024-03-18 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_waitinglist_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='registration_token',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]