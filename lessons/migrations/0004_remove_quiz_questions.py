# Generated by Django 5.0.1 on 2024-03-11 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_quiz_questions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='questions',
        ),
    ]
